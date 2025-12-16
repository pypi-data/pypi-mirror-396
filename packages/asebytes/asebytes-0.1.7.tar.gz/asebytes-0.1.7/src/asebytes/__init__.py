import importlib.metadata

from .decode import decode
from .encode import encode
from .io import ASEIO, BytesIO
from .metadata import get_metadata

__all__ = ["encode", "decode", "BytesIO", "ASEIO", "get_metadata"]

__version__ = importlib.metadata.version("asebytes")
