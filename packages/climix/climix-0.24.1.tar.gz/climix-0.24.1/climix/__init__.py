# -*- coding: utf-8 -*-

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("climix")
except PackageNotFoundError:
    # package is not installed
    pass

__all__ = [
    "__version__",
]
