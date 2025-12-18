from .ouisparql import from_path, from_str, register_adapter
from .utils import SPARQLParseException, SPARQLLoadException
from importlib.metadata import version

__version__ = version("ouisparql")

__all__ = [
    "from_path",
    "from_str",
    "register_adapter",
    "SPARQLParseException",
    "SPARQLLoadException",
]
