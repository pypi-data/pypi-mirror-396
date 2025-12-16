import os
from uuid import uuid4
import numpy as np


OUT_BASE_PATH = "/tmp/data/out"


def read_array_file(path: str, shape: tuple, dtype: str):
    with open(path, "rb") as fp:
        data = fp.read()
    array = np.frombuffer(data, dtype=dtype)
    array = array.reshape(shape)

    return array


def write_array_file(data: np.ndarray) -> str:
    path = os.path.join(OUT_BASE_PATH, str(uuid4()))
    with open(path, "wb") as fp:
        b = data.tobytes()
        fp.write(b)
    return path, data.shape, data.dtype.descr[0][1]
