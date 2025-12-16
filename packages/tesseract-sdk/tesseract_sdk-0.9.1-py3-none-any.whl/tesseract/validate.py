import tempfile
import json
import pathlib
import numpy as np
from matplotlib.pyplot import imsave
from typing import Dict, List
from rich.console import Console
from rich.table import Table
import rich
from tesseract import inference_pb2, inference_pb2_grpc
from tesseract.inference_pb2 import google_dot_protobuf_dot_empty__pb2

import geodesic
from geodesic.tesseract import Job

try:
    import docker
except ImportError:
    raise Exception(
        "to run validation you must have docker installed.\n\t pip install docker"
    )
try:
    import grpc
except ImportError:
    raise Exception(
        "to run validation you must have grpc installed.\n\t pip install grpcio"
    )

empty = google_dot_protobuf_dot_empty__pb2.Empty()


class ValidationManager(object):
    def __init__(
        self,
        image: str = None,
        test_data: str = None,
        asset_bands: List[Dict] = None,
        output_asset_bands: List[Dict] = [],
        save_output: bool = False,
        cli: bool = False,
        args=None,
        print_container_logs=False,
    ):
        self.gutenberger = Gutenberger()
        self.image = image
        self.input_assets = None
        self.output_assets = None
        self.cli = cli
        self.asset_bands = None
        self.output_asset_bands = output_asset_bands
        self.save_output = save_output
        self.print_container_logs = print_container_logs
        self.args = args

        self.test_data = None
        # if test data is already a url, just use it, if its a tesseract job, query tesseract and get the path
        if isinstance(test_data, str):
            self.test_data = test_data
        elif isinstance(test_data, dict):
            try:
                geodesic.set_active_project(test_data["project"])
                job = Job(job_id=test_data["job_id"])
                self.test_data = job._item["assets"]["zarr-root"]["href"]
            except ValueError:
                raise ValueError(
                    "test_data must be a valid tesseract job id or a gs:// url"
                )

        self.test_data = None
        # if test data is already a url, just use it, if its a tesseract job, query tesseract and get the path
        if isinstance(test_data, str):
            self.test_data = test_data
        elif isinstance(test_data, dict):
            try:
                geodesic.set_active_project(test_data["project"])
                job = Job(job_id=test_data["job_id"])
                self.test_data = job._item["assets"]["zarr-root"]["href"]
            except ValueError:
                raise ValueError(
                    "test_data must be a valid tesseract job id or a gs:// url"
                )

        if self.output_asset_bands is not None:
            for oa_bands in self.output_asset_bands:
                if not (len(oa_bands["bands"]) == 1 or len(oa_bands["bands"]) == 3):
                    raise ValueError(
                        "output_asset_bands must be either length 1 or 3 to write out an validation image."
                    )

        # asset_bands is in the same format as Tesseract which is a list of dictionaries. Changing
        # it to be a dict with keys of the input names just to make things easier to get later.
        if asset_bands is not None:
            self.asset_bands = {}
            list_of_assets = []
            for asset_band in asset_bands:
                self.asset_bands[asset_band["asset_name"]] = asset_band["bands"]
                if asset_band["asset_name"] in list_of_assets:
                    raise ValueError(
                        f"Cannot have duplicate assets in asset_bands input. Duplicate: {asset_band['asset_name']}"
                    )
                list_of_assets.append(asset_band["asset_name"])

        tmp_dir = tempfile.mkdtemp()
        self.tmp_path = pathlib.Path(tmp_dir)
        self.data_path = self.tmp_path / "data"
        (self.tmp_path / "data" / "out").mkdir(exist_ok=True, parents=True)
        (self.tmp_path / "data" / "in").mkdir(exist_ok=True, parents=True)
        (self.tmp_path / "log").mkdir(exist_ok=True)

        # run() will call these tests in order
        self.tests = [self.test_model_info, self.test_model_data]

        # will be reported in a summary at the end.
        self.stats = {"tests": 0, "passed": 0, "warnings": 0, "failed": 0}

        if self.test_data:
            try:
                import zarr
            except ImportError:
                raise ImportError(
                    "Zarr must be installed to use the 'test_data' option.  (pip install zarr)"
                )

        if self.save_output:
            # create local zarr file
            self.out_zf = zarr.open("./validation_output/output.zarr", "w")

    def __del__(self):
        try:
            self.gutenberger.section("Cleaning Up")
            self.gutenberger.task("Killing Model Container")
        except Exception:
            print("Cleaning Up")
            print("Killing model container")
            pass

        logs = None
        if self.print_container_logs:
            try:
                logs = self.model_container.logs().decode()
            except docker.errors.NotFound:
                pass

        try:
            self.model_container.kill()
        except docker.errors.APIError:
            pass

        try:
            self.model_container.remove()
        except docker.error.APIError as e:
            raise (e)

        try:
            self.gutenberger.summary(stats=self.stats, logs=logs)

        except Exception:
            pass

    def model(self, status):
        status.update("[orange_red1]Starting Model Container")
        docker_client = docker.from_env()
        try:
            environment = {"MODEL_CONTAINER_GRPC_PORT": 50051}
            if self.args:
                environment["MODEL_ARGS"] = self.args

            self.model_container = docker_client.containers.run(
                image=self.image,
                ports={50051: 50051},
                environment=environment,
                volumes={
                    self.tmp_path: {"bind": "/tmp", "mode": "rw"},
                },
                detach=True,
            )
        except Exception:
            raise Exception(
                "could not start container", self.model_container.logs().decode()
            )

        try:
            _ = docker_client.containers.get(self.model_container.name)
        except docker.errors.NotFound:
            raise Exception(
                "could not find running container", self.model_container.logs().decode()
            )
        self.gutenberger.task("Model Container Running")

    def grpc_client(self, status):
        status.update("[orange_red1]Waiting for connection to container")
        self.channel = grpc.insecure_channel("localhost:50051")
        try:
            grpc.channel_ready_future(self.channel).result(timeout=45)
        except grpc.FutureTimeoutError:
            self.gutenberger.task(
                "[red]could not connect to the model container. GRPC Timeout. Docker logs:"
            )
            self.model_container.remove
            print(self.model_container.logs().decode())
            exit(1)
        except Exception as e:
            self.gutenberger.task(
                "[red]could not connect to the model container. Docker logs:"
            )
            print(self.model_container.logs().decode())
            raise (e)
        self.client = inference_pb2_grpc.InferenceServiceV1Stub(self.channel)
        self.gutenberger.task("Connection established")

    def test_model_info(self, status) -> list:
        status.update("[orange_red1]Test Get Model Info")
        result = []
        n_tests = 0
        try:
            n_tests += 1
            resp = self.client.GetModelInfo(empty)
        except Exception as e:
            self.gutenberger.test_status("Get Model Info", "Failed")
            result.append(e)
            return result, n_tests

        input_state = "Passed"
        n_tests += 1
        try:
            self.input_assets = []
            for asset in resp.inputs:
                self.input_assets.append(
                    {"name": asset.name, "shape": asset.shape, "dtype": asset.dtype}
                )
            if len(self.input_assets) < 1:
                result.append("model info must return at least one input asset")
                input_state = "Failed"
        except Exception as e:
            result.append(e)
            input_state = "Failed"

        self.gutenberger.test_status("Check model info inputs", input_state)

        output_state = "Passed"
        n_tests += 1
        try:
            self.output_assets = []
            for asset in resp.outputs:
                self.output_assets.append(
                    {"name": asset.name, "shape": asset.shape, "dtype": asset.dtype}
                )
            if len(self.output_assets) < 1:
                result.append("model info must return at least one output asset")
                output_state = "Failed"
        except Exception as e:
            result.append(e)
            output_state = "Failed"

        self.gutenberger.test_status("Check model info outputs", output_state)

        return result, n_tests

    def make_data(self, status):
        if self.test_data is not None:
            try:
                import zarr
            except ImportError:
                raise ImportError(
                    "Zarr must be installed to use the 'test_data' option.  (pip install zarr)"
                )
            status.update(f"[orange_red1]Reading data from {self.test_data}")
            zf = zarr.open(self.test_data, "r")

        else:
            status.update("[orange_red1]Creating Data for Inference Test")

        for info in self.input_assets:
            if info["shape"] is not None and len(info["shape"]) > 0:
                if self.test_data is not None:
                    zf_shape = zf[info["name"]]["tesseract"].shape
                    if zf_shape < tuple(info["shape"]):
                        raise ValueError(
                            f"Zarr file shape is smaller than the requested data input size. File Shape: {zf_shape},  Requested Shape: {tuple(info['shape'])}"
                        )

                    # check that the dtype of the zarr file matches the model info spec
                    if zf[info["name"]]["tesseract"].dtype != np.dtype(info["dtype"]):
                        raise ValueError(
                            f"Input asset dtype does not match the model info spec for {info['name']}. Input dtype: {zf[info['name']]['tesseract'].dtype},  Model Info dtype: {np.dtype(info['dtype'])}"
                        )

                    # check that the dtype of the zarr file matches the model info spec
                    if zf[info["name"]]["tesseract"].dtype != np.dtype(info["dtype"]):
                        raise ValueError(
                            f"Input asset dtype does not match the model info spec for {info['name']}. Input dtype: {zf[info['name']]['tesseract'].dtype},  Model Info dtype: {np.dtype(info['dtype'])}"
                        )

                    arr = zf[info["name"]]["tesseract"][
                        0 : info["shape"][0],
                        :,
                        0 : info["shape"][2],
                        0 : info["shape"][3],
                    ]
                    arr = arr[:, self.asset_bands[info["name"]]]

                    x = zf[info["name"]]["x"][0 : info["shape"][3]]
                    y = zf[info["name"]]["y"][0 : info["shape"][2]]
                    t = zf[info["name"]]["times"][0 : info["shape"][0]]
                else:
                    arr = (100 * np.random.rand(*info["shape"])).astype(
                        dtype=info["dtype"]
                    )
                    x = np.arange(0, info["shape"][3], 1.0, dtype="<f8")
                    y = np.arange(0, info["shape"][2], 1.0, dtype="<f8")
                    start_date = np.datetime64("2020-01-01")
                    end_date = np.datetime64("2020-01-01") + (
                        np.timedelta64(info["shape"][0], "D")
                    )
                    times = np.arange(start_date, end_date, np.timedelta64(1, "D"))
                    t = np.empty(shape=(times.shape[0], 2), dtype="datetime64[ns]")
                    for i, bin_start in enumerate(times):
                        t[i] = [bin_start, bin_start + np.timedelta64(1, "D")]
                arr_bts = arr.tobytes()
                x_bts = x.tobytes()
                y_bts = y.tobytes()
                times_bts = t.tobytes()
                with open(self.data_path / "in" / f"{info['name']}.dat", "wb") as fp:
                    fp.write(arr_bts)
                with open(
                    self.data_path / "in" / f"{info['name']}[grid-x].dat", "wb"
                ) as fp:
                    fp.write(x_bts)
                with open(
                    self.data_path / "in" / f"{info['name']}[grid-y].dat", "wb"
                ) as fp:
                    fp.write(y_bts)
                with open(
                    self.data_path / "in" / f"{info['name']}[grid-t].dat", "wb"
                ) as fp:
                    fp.write(times_bts)
            else:
                with open(self.data_path / "in" / f"{info['name']}.geojson", "w") as fp:
                    json.dump(
                        geodesic.FeatureCollection(
                            type="FeatureCollection", features=[]
                        ),
                        fp,
                    )
        self.gutenberger.task("Test data created")

    def test_model_data(self, status):
        result = []
        n_tests = 0
        self.make_data(status)
        status.update("[orange_red1]Test Model Inference")
        message = []

        for index, info in enumerate(self.input_assets):
            if info["shape"] is not None and len(info["shape"]) > 0:
                for part in ["", "[grid-x]", "[grid-y]", "[grid-t]"]:
                    type_ = "tensor"
                    filepath = f"/tmp/data/in/{info['name']}{part}.dat"
                    if part == "[grid-x]":
                        shape = [info["shape"][3]]
                        dtype = "<f8"
                    elif part == "[grid-y]":
                        shape = [info["shape"][2]]
                        dtype = "<f8"
                    elif part == "[grid-t]":
                        shape = [info["shape"][0], 2]
                        dtype = "datetime64[ns]"
                    elif part == "":
                        shape = info["shape"]
                        dtype = info["dtype"]

                    message.append(
                        inference_pb2.SendAssetDataRequest(
                            name=f"{info['name']}{part}",
                            type=type_,
                            header=inference_pb2.AssetDataHeader(
                                shape=shape, dtype=dtype, filepath=filepath
                            ),
                            index=index,
                        )
                    )
            else:
                type_ = "features"
                filepath = f"/tmp/data/in/{info['name']}.geojson"

                message.append(
                    inference_pb2.SendAssetDataRequest(
                        name=info["name"],
                        type=type_,
                        header=inference_pb2.AssetDataHeader(
                            shape=info["shape"], dtype=info["dtype"], filepath=filepath
                        ),
                        index=index,
                    )
                )

        try:
            response = self.client.SendAssetData(iter(message))
        except Exception as e:
            result.append(e)
            return result, n_tests

        try:
            resp_iter = list(iter(response))
        except Exception as e:
            print("Model Container Logs:")
            print(self.model_container.logs().decode())
            result.append(e)
            return result, n_tests

        for resp in resp_iter:
            n_tests += self.test_response(resp, result, n_tests)

        return result, n_tests

    def test_response(self, resp, result, n_tests) -> int:
        resp_names = []
        keys_state = "Passed"
        n_tests += 1
        if resp.name.startswith("$"):
            index = int(resp.name[1:])
            resp.name = self.output_assets[index]["name"]
        elif resp.name not in self.output_assets:
            keys_state = "Failed"
            self.gutenberger.test_status(
                f"returned name {resp.name} not found in model info outputs", keys_state
            )
            print(self.model_container.logs().decode())
            raise ValueError("Response name not found in model info outputs")

        resp_names.append(resp.name)
        idx = -1
        for i, info in enumerate(self.output_assets):
            if info["name"] == resp.name:
                idx = i
                break

        expected_asset = self.output_assets[idx]

        if expected_asset["dtype"]:
            return self.test_tensor_response(resp, expected_asset, result, n_tests)
        else:
            return self.test_features_response(resp, expected_asset, result, n_tests)

    def test_features_response(self, resp, expected_asset, result, n_tests) -> int:
        load_geojson_state = "Passed"

        # Read file and check that you can parse it into the correct shape
        file_name = resp.header.filepath.split("out")[-1].strip("/")
        file_path = str(self.data_path / "out" / file_name)
        n_tests += 1
        try:
            fc = geodesic.FeatureCollection.from_geojson_file(file_path)
            assert "type" in fc
            assert "features" in fc
        except Exception as e:
            result.append(Exception(f"unable to load geojson features: {str(e)}"))
            load_geojson_state = "Failed"

        self.gutenberger.test_status(
            f"({resp.name}) Check valid GeoJSON", load_geojson_state
        )
        return n_tests

    def test_tensor_response(self, resp, expected_asset, result, n_tests) -> int:
        # TODO: Write out image output so that it can be checked if a validate config is supplied.
        dtype_state = "Passed"
        n_tests += 1
        if np.dtype(resp.header.dtype) != np.dtype(expected_asset["dtype"]):
            result.append(
                Exception(
                    f"response dtype {resp.header.dtype} does not match expected"
                    f" dtype {expected_asset['dtype']} for {resp.name}"
                )
            )
            dtype_state = "Failed"
            self.gutenberger.test_status(
                f"({resp.name}) Check returned dtype", dtype_state
            )
            return n_tests
        else:
            self.gutenberger.test_status(
                f"({resp.name}) Check returned dtype", dtype_state
            )

        # Read file and check that you can parse it into the correct shape
        file_name = resp.header.filepath.split("out")[-1].strip("/")
        file_path = str(self.data_path / "out" / file_name)
        raw_output = np.fromfile(file_path, dtype=resp.header.dtype)

        reshape_state = "Passed"
        n_tests += 1
        try:
            test_arr = np.reshape(raw_output, resp.header.shape)

        except Exception as e:
            result.append(e)
            reshape_state = "Failed"
            self.gutenberger.test_status(
                f"({resp.name}) Check data is reshapeable", reshape_state
            )
            return n_tests

        shape_state = "Passed"
        n_tests += 1
        if test_arr.shape != tuple(expected_asset["shape"]):
            result.append(
                f"response shape {resp.header.shape} did not match "
                f"expected shape {expected_asset['shape']} for {resp.name}"
            )
            shape_state = "Failed"
            self.gutenberger.test_status(
                f"({resp.name}) Check returned shape", shape_state
            )
        else:
            self.gutenberger.test_status(
                f"({resp.name}) Check returned shape", shape_state
            )

        for output_asset in self.output_asset_bands:
            if output_asset["asset_name"] != resp.name:
                continue
            try:
                # Write out images here if defined
                if len(expected_asset["shape"]) == 4:
                    img_output = test_arr[0, output_asset["bands"], :, :]
                    img_output = np.moveaxis(img_output, 0, 2)
                else:
                    img_output = test_arr[output_asset["bands"], :, :].squeeze()
                img_path = pathlib.Path("./validation_output")
                img_path.mkdir(parents=True, exist_ok=True)
                img_name = f"{resp.name}_{'-'.join([str(b) for b in output_asset['bands']])}.png"
                if img_output.shape[2] == 1:
                    img_output = img_output.squeeze()
                imsave(str(img_path / img_name), arr=img_output)
                self.gutenberger.task(
                    f"validation image written out to {img_path}/{img_name}"
                )
            except Exception as e:
                self.gutenberger.test_status(
                    f"({resp.name}) Could not write out validation image, {e}",
                    "warning",
                )
                self.stats["warnings"] += 1

        if self.save_output:
            try:
                self.out_zf.array(name=resp.name, data=test_arr)
            except Exception as e:
                self.gutenberger.test_status(
                    f"({resp.name}) Could not write out zarr array", "warning"
                )
                self.stats["warnings"] += 1

        return n_tests

    def run(self):
        """Run all of the setup and tests here."""
        self.gutenberger.header(f"Testing image {self.image}")
        self.gutenberger.section("Setting Up Tests")

        status = self.gutenberger.thinking("")
        with status:
            self.model(status)
            self.grpc_client(status)

        self.gutenberger.section("Running Tests")
        test_status = self.gutenberger.thinking("")
        with test_status:
            for test in self.tests:
                result, n_tests = test(test_status)
                self.stats["tests"] += n_tests
                self.stats["passed"] += n_tests - len(result)
                self.stats["failed"] += len(result)
                if len(result) > 0:
                    for res in result:
                        print(f"test_result: {res}")
                    break

        if not self.cli:
            self.__del__()


class Gutenberger:
    def __init__(self):
        self.c = Console()

    def header(self, message):
        banner_colored = rich.text.Text(
            r"""[blue]
 ______                                                     __      
[purple]/[blue]\__  _\                                                   [purple]/[blue]\ \__   
[purple]\/_/[blue]\ \\[purple]/    [blue]__    ____    ____     __   _ __    __      ___[purple]\ [blue]\ ,_\  
   [purple]\ [blue]\ \  /'__`\ /',__\  /',__\  /'__`\\[purple]/[blue]\`'__\/'__`\   /'___\ \ \\[purple]/[blue]  
    [purple]\ [blue]\ \\[purple]/[blue]\  __/[purple]/[blue]\__, `\\[purple]/[blue]\__, `\\[purple]/[blue]\  __/[purple]\ [blue]\ \\[purple]//[blue]\ \\[purple]L[blue]\.\_[purple]/[blue]\ \__[purple]/\ [blue]\ \_ 
     [purple]\ [blue]\_\ \____\\[purple]/[blue]\____/[purple]\/[blue]\____/[purple]\ [blue]\____\\[purple]\ [blue]\_\\[purple]\ [blue]\__/[purple].[blue]\_\ \____\\[purple]\ [blue]\__\
      [purple]\/_/\/____/\/___/  \/___/  \/____/ \/_/ \/__/\/_/\/____/ \/__/   [purple]A SeerAI Joint
                                                                   
"""
        )
        # Keeping the regular banner in here because its impossible to make sense of the colored one.
        banner = rich.text.Text(
            r"""[blue]
 ______                                                     __      
/\__  _\                                                   /\ \__   
\/_/\ \/    __    ____    ____     __   _ __    __      ___\ \ ,_\  
   \ \ \  /'__`\ /',__\  /',__\  /'__`\/\`'__\/'__`\   /'___\ \ \/  
    \ \ \/\  __//\__, `\/\__, `\/\  __/\ \ \//\ \L\.\_/\ \__/\ \ \_ 
     \ \_\ \____\/\____/\/\____/\ \____\\ \_\\ \__/.\_\ \____\\ \__\
      \/_/\/____/\/___/  \/___/  \/____/ \/_/ \/__/\/_/\/____/ \/__/   [purple]A SeerAI Joint
                                                                   
"""
        )
        self.c.print(f"{banner_colored}", style="blue")
        self.c.print(f"[bold red]*** {message} ***\n", justify="center")

    def thinking(self, message):
        return self.c.status(f"[green]{message}", spinner="aesthetic")

    def task(self, message):
        self.c.print(f"[green]{message}")

    def test_status(self, message, state):
        if state == "Passed":
            color = "[green]"
        elif state == "Failed":
            color = "[red]"
        else:
            color = "[orange_red1]"
        self.c.print(f"[green]{message} [dark_violet]... {color}{state}")

    def section(self, message):
        self.c.rule(f"[bold red]{message}", style="blue")

    def summary(self, stats: dict = {}, logs: str = None):
        if logs is not None:
            self.section("Container Logs")
            print(logs)
        self.c.rule("[orange_red1]Summary", characters="=")
        table = Table(show_footer=False, box=rich.box.HEAVY, style="blue")
        table_centered = rich.align.Align.center(table)
        table.add_column("Tests", style="green", justify="center")
        table.add_column("Passed", style="green", justify="center")
        table.add_column("Warnings", style="orange_red1", justify="center")
        table.add_column("Failed", style="red", justify="center")

        table.add_row(
            str(stats["tests"]),
            str(stats["passed"]),
            str(stats["warnings"]),
            str(stats["failed"]),
        )
        self.c.print(table_centered)
