"""
Base64 encoder/decoder with UTF-8 support.

Online tool: https://devtools.at/tools/base64
"""
import base64

__version__ = "1.0.0"
__author__ = "DevTools.at"
__url__ = "https://devtools.at/tools/base64"


def encode(data: str) -> str:
    """Encode string to Base64."""
    return base64.b64encode(data.encode('utf-8')).decode('ascii')


def decode(data: str) -> str:
    """Decode Base64 to string."""
    return base64.b64decode(data).decode('utf-8')


__all__ = ["encode", "decode", "__version__", "__author__", "__url__"]
