import os
import json
import re
import uuid
import inspect
import traceback
import logging
from time import time
from types import FunctionType
from typing import Iterator, Union
from functools import partial
from collections import defaultdict
from concurrent import futures

import geodesic
import geopandas as gpd
import grpc
import numpy as np

from tesseract.inference_pb2_grpc import (
    InferenceServiceV1Servicer,
    add_InferenceServiceV1Servicer_to_server,
)
from tesseract.inference_pb2 import (
    ModelInfo,
    SendAssetDataResponse,
    SendAssetDataRequest,
    AssetDataHeader,
    AssetDataInfo,
)
from tesseract.tensor import read_array_file, write_array_file
from tesseract.features import read_geojson_file, write_geojson_file
from tesseract._logging import _get_logger, _child_logger


def get_model_args() -> dict:
    model_args = {}
    if os.getenv("MODEL_ARGS") is not None:
        try:
            model_args = json.loads(os.getenv("MODEL_ARGS"))
        except json.decoder.JSONDecodeError:
            pass
    return model_args


os.makedirs("/tmp/log/", exist_ok=True)
logger = _get_logger(__name__)

grid_re = re.compile(r"\[grid\-(x|y|t)\]")


class TesseractModelServicer(InferenceServiceV1Servicer):
    def __init__(self, inference_func, model_info_func):
        self.inference_func = inference_func
        if not callable(inference_func):
            raise ValueError("inference_func must be a callable")

        self.model_info_func = model_info_func
        if not callable(model_info_func):
            raise ValueError("model_info_fun must be a callable")

        self.model_info = self.model_info_func()
        self.asset_types = {}
        for input in self.model_info["inputs"]:
            self.asset_types[input["name"]] = input.get("type")

        self.output_asset_names = [output["name"] for output in self.model_info["outputs"]]

        self.model_args = get_model_args()
        self.send_args = False
        self.send_grids = False
        signature = inspect.signature(inference_func)
        for key, param in signature.parameters.items():
            if key == "grids":
                self.send_grids = True
                continue
            if param.kind == param.VAR_KEYWORD:
                if self.model_args:
                    self.send_args = True

    def GetModelInfo(self, request: None, context: grpc.ServicerContext) -> ModelInfo:
        model_info = self.model_info_func()

        # Get all of the inputs required by the model
        model_inputs = []
        for input in model_info["inputs"]:
            i = AssetDataInfo(
                name=input["name"], shape=input.get("shape"), dtype=input.get("dtype")
            )
            model_inputs.append(i)

        # Get all of the outputs the model will return
        model_outputs = []
        for input in model_info["outputs"]:
            i = AssetDataInfo(
                name=input["name"], shape=input.get("shape"), dtype=input.get("dtype")
            )
            model_outputs.append(i)

        res = ModelInfo(inputs=model_inputs, outputs=model_outputs)
        return res

    def SendAssetData(
        self, request: Iterator[SendAssetDataRequest], context: grpc.ServicerContext
    ) -> Iterator[SendAssetDataResponse]:
        user_logger = _child_logger(logger, "model", f"/tmp/log/{uuid.uuid4()}.log")

        logger.debug("receiving SendAssetDataRequest")
        try:
            in_assets, grids = self.read_asset_data(request, context)
        except Exception as e:
            yield error_response(
                e, "invalid argument", grpc.StatusCode.INVALID_ARGUMENT, logger, context
            )
            return

        try:
            logger.info("running inference_func")
            t = time()

            inference_func = self.inference_func
            if self.send_args:
                inference_func = partial(inference_func, **self.model_args)
            if self.send_grids:
                inference_func = partial(inference_func, grids=grids)

            out_assets = inference_func(assets=in_assets, logger=user_logger)
            logger.info(f"Done, inference_func finished in {time() - t} s")
        except Exception as e:
            yield error_response(e, "inference failed", grpc.StatusCode.INTERNAL, logger, context)
            return

        logger.debug("sending SendAssetDataResponse")
        for name, out_asset in out_assets.items():
            out_asset_name = self.convert_asset_name(name)
            logger.debug(f"writing out asset '{name}' as '{out_asset_name}'")

            if isinstance(out_asset, (dict, geodesic.FeatureCollection, gpd.GeoDataFrame)):
                yield self.get_feature_response(out_asset_name, out_asset)
            elif isinstance(out_asset, np.ndarray):
                yield self.get_tensor_response(out_asset_name, out_asset)
            else:
                yield error_response(
                    None,
                    f"invalid data returned for asset {name} from inference function",
                    grpc.StatusCode.INTERNAL,
                    logger,
                    context,
                )
                return

        logger.debug("inference finished")
        for handler in user_logger.handlers:
            handler.flush()

    def convert_asset_name(self, asset_name: str) -> str:
        if asset_name.startswith("$"):
            return asset_name
        return f"${self.output_asset_names.index(asset_name)}"

    def read_asset_data(
        self, request: Iterator[SendAssetDataRequest], context: grpc.ServicerContext
    ) -> dict:
        # Parsed asset data
        in_assets = {}
        grids = defaultdict(dict)

        # Get all the assets from the stream
        for req in request:
            name = req.name
            type_ = req.type
            header = req.header
            index = req.index
            grid_for_index = req.grid_for_index

            if header is None:
                raise ValueError("empty header received")

            logger.debug(f"received asset '{name}'")

            if type_ != "tensor" and type_ != "features":
                exc_msg = f"asset '{name}' invalid type {type_}. Must be 'tensor' or 'features'"
                logger.error(exc_msg)
                raise ValueError(exc_msg)

            # Get info from the header
            filepath = header.filepath
            shape = header.shape
            dtype = header.dtype

            if type_ == "tensor":
                asset_data = read_array_file(filepath, shape, dtype)
            elif type_ == "features":
                asset_data = read_geojson_file(filepath)

            # Is this a grid asset?
            m = grid_re.search(name)
            if m is not None:
                asset_name_end, _ = m.span()
                dimension = m.group(1)
                asset_name = name[:asset_name_end]
                grids[asset_name][dimension] = asset_data
                grids[f"${grid_for_index}"][dimension] = asset_data
                logger.debug(f"read {asset_name} grid dimension {dimension}'")
            else:
                in_assets[name] = asset_data
                in_assets[f"${index}"] = asset_data
                logger.debug(f"read asset '{name}'")

        return in_assets, grids

    def get_feature_response(
        self, name: str, out_asset: Union[dict, geodesic.FeatureCollection, gpd.GeoDataFrame]
    ) -> SendAssetDataResponse:
        if isinstance(out_asset, gpd.GeoDataFrame):
            out_asset = out_asset.__geo_interface__
        filepath = write_geojson_file(out_asset)

        return SendAssetDataResponse(
            name=name, type="features", header=AssetDataHeader(filepath=filepath)
        )

    def get_tensor_response(self, name: str, out_asset: np.ndarray) -> SendAssetDataResponse:
        filepath, shape, dtype = write_array_file(out_asset)
        return SendAssetDataResponse(
            name=name,
            type="tensor",
            header=AssetDataHeader(filepath=filepath, shape=shape, dtype=dtype),
        )


def error_response(
    e: Exception,
    msg: str,
    code: grpc.StatusCode,
    logger: logging.Logger,
    context: grpc.ServicerContext,
) -> SendAssetDataResponse:
    extra = None
    tb = msg
    if e is not None:
        tb = traceback.format_exc()
        extra = {"error": tb}
    logger.error(msg, extra=extra)
    context.set_code(code)
    context.set_details(tb)
    return SendAssetDataResponse()


def serve(inference_func: FunctionType, model_info_func: FunctionType) -> grpc.Server:
    logger.info("initializing server")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = TesseractModelServicer(
        inference_func=inference_func, model_info_func=model_info_func
    )
    add_InferenceServiceV1Servicer_to_server(servicer, server)

    port = os.getenv("MODEL_CONTAINER_GRPC_PORT")
    if port is None or port == "":
        port = "8081"
    logger.info("initializing starting server on %s", f"[::]:{port}")
    server.add_insecure_port(f"[::]:{port}")
    server.start()

    logger.info("server started")
    server.wait_for_termination()
