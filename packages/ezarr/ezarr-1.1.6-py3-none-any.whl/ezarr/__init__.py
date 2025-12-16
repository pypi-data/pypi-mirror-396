import importlib

from ezarr import inplace, io
from ezarr.dict import EZDict
from ezarr.list import EZList
from ezarr.types import PyObject, PyObjectCodec, SupportsEZRead, SupportsEZReadWrite, SupportsEZWrite

importlib.import_module("ezarr.patch")

__all__ = [
    "inplace",
    "EZDict",
    "EZList",
    "io",
    "PyObject",
    "PyObjectCodec",
    "SupportsEZRead",
    "SupportsEZReadWrite",
    "SupportsEZWrite",
]
