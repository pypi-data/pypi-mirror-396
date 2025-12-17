# src/anypoint_sdk/_version.py
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("anypoint-sdk")
except PackageNotFoundError:
    # Package is not installed yet, e.g. when running from a source checkout
    __version__ = "0.0.0"
