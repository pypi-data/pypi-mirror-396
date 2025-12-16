"""Quantmaster: features quantitativas para algorithmic trading."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("quantmaster")
except PackageNotFoundError:
    __version__ = "0.0.0"
