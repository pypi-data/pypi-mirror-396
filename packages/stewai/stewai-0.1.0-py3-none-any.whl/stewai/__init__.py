from importlib.metadata import PackageNotFoundError, version

from .client import Stew

try:
    __version__ = version("stewai")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = ["Stew", "__version__"]
