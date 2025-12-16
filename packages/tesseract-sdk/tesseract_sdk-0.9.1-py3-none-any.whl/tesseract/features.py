import os
import json
from uuid import uuid4
from typing import Union

import geodesic


OUT_BASE_PATH = "/tmp/data/out"


def read_geojson_file(path: Union[str, os.PathLike]) -> geodesic.FeatureCollection:
    return geodesic.FeatureCollection.from_geojson_file(path)


def write_geojson_file(fc: geodesic.FeatureCollection) -> str:
    path = os.path.join(OUT_BASE_PATH, str(uuid4()))
    with open(path, "w") as fp:
        json.dump(fc, fp)

    return path
