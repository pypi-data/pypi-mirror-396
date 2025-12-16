import importlib
from sys import stderr
import sys

try:
    importlib.import_module("pandas")

except ModuleNotFoundError:
    print("Please install ezarr[pandas] to use dataframes", file=stderr)
    sys.exit(1)


from ezarr.dataframe.dataframe import EZDataFrame

importlib.import_module("ezarr.dataframe.patch")


__all__ = ["EZDataFrame"]
