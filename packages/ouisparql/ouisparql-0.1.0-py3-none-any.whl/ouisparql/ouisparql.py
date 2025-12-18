from pathlib import Path
from typing import Callable, Dict, Optional, Type, Union, Tuple, List, Any

from .adapters.generic import GenericAdapter
from .adapters.sparqlwrapper import SPARQLWrapperAdapter
from .utils import SPARQLLoadException, log
from .queries import Queries
from .query_loader import QueryLoader
from .types import DriverAdapterProtocol

_ADAPTERS: Dict[str, Callable[..., DriverAdapterProtocol]] = {
    "sparql_wrapper": SPARQLWrapperAdapter
}
"""Map adapter names to their adapter class."""


def register_adapter(name: str, adapter: Callable[..., DriverAdapterProtocol]):
    """Register or override an adapter."""
    if name.lower() in _ADAPTERS:
        log.debug(f"overriding aiosparql adapter {name}")
    _ADAPTERS[name.lower()] = adapter


def _make_driver_adapter(
    driver_adapter: Union[str, Callable[..., DriverAdapterProtocol]], *args, **kwargs
) -> DriverAdapterProtocol:
    """Get the driver adapter instance registered by the `driver_name`."""
    if isinstance(driver_adapter, str):
        try:
            adapter = _ADAPTERS[driver_adapter.lower()]
        except KeyError:
            raise ValueError(
                f"Encountered unregistered driver_adapter: {driver_adapter}"
            )
    # so, can we just call it?
    elif callable(driver_adapter):  # pragma: no cover
        adapter = driver_adapter
    else:
        raise ValueError(f"Unexpected driver_adapter: {driver_adapter}")
    return adapter(*args, **kwargs)


def from_str(
    sparql: str,
    driver_adapter: Union[str, Callable[..., DriverAdapterProtocol]],
    record_classes: Optional[Dict] = None,
    kwargs_only: bool = True,
    attribute: Optional[str] = "__",
    args: List[Any] = [],
    kwargs: Dict[str, Any] = {},
    loader_cls: Type[QueryLoader] = QueryLoader,
    queries_cls: Type[Queries] = Queries,
):
    """Load queries from a SPARQL string.

    **Parameters:**

    - **sparql** - A string containing SPARQL statements and aiosparql name.
    - **driver_adapter** - Either a string to designate one of the aiosparql built-in database driver
      adapters. One of many available for SPARQLite, Postgres and MySPARQL. If you have defined your
      own adapter class, you can pass it's constructor.
    - **kwargs_only** - *(optional)* whether to only use named parameters on query execution, default is *True*.
    - **attribute** - *(optional)* ``.`` attribute access substitution, defaults to ``"__"``, *None* disables
      the feature.
    - **args** - *(optional)* adapter creation args (list), forwarded to cursor creation by default.
    - **kwargs** - *(optional)* adapter creation args (dict), forwarded to cursor creation by default.
    - **record_classes** - *(optional)* **DEPRECATED** Mapping of strings used in "record_class"
      declarations to the python classes which aiosparql should use when marshaling SPARQL results.
    - **loader_cls** - *(optional)* Custom constructor for QueryLoader extensions.
    - **queries_cls** - *(optional)* Custom constructor for Queries extensions.

    **Returns:** ``Queries``

    Usage:

    Loading queries from a SPARQL string.

    .. code-block:: python

      import sparqlite3
      import aiosparql

      sparql_text = \"\"\"
      -- name: get-all-greetings
      -- Get all the greetings in the database
      select * from greetings;

      -- name: get-user-by-username^
      -- Get all the users from the database,
      -- and return it as a dict
      select * from users where username = :username;
      \"\"\"

      queries = aiosparql.from_str(sparql_text, "sparqlite3")
      queries.get_all_greetings(conn)
      queries.get_user_by_username(conn, username="willvaughn")
    """
    adapter = _make_driver_adapter(driver_adapter, *args, **kwargs)
    query_loader = loader_cls(adapter, record_classes, attribute=attribute)
    query_data = query_loader.load_query_data_from_sparql(sparql, [])
    return queries_cls(adapter, kwargs_only=kwargs_only).load_from_list(query_data)


def from_path(
    sparql_path: Union[str, Path],
    driver_adapter: Union[str, Callable[..., DriverAdapterProtocol]],
    record_classes: Optional[Dict] = None,
    kwargs_only: bool = True,
    attribute: Optional[str] = "__",
    args: List[Any] = [],
    kwargs: Dict[str, Any] = {},
    loader_cls: Type[QueryLoader] = QueryLoader,
    queries_cls: Type[Queries] = Queries,
    ext: Tuple[str] = (".rq",),
    encoding=None,
):
    """Load queries from a `.rq` file, or directory of `.rq` files.

    **Parameters:**

    - **sparql_path** - Path to a `.rq` file or directory containing `.rq` files.
    - **driver_adapter** - Either a string to designate one of the aiosparql built-in database driver
      adapters. One of many available for SPARQLite, Postgres and MySPARQL. If you have defined your own
      adapter class, you may pass its constructor.
    - **record_classes** - *(optional)* **DEPRECATED** Mapping of strings used in "record_class"
    - **kwargs_only** - *(optional)* Whether to only use named parameters on query execution, default is *True*.
    - **attribute** - *(optional)* ``.`` attribute access substitution, defaults to ``"__""``, *None* disables
      the feature.
    - **args** - *(optional)* adapter creation args (list), forwarded to cursor creation by default.
    - **kwargs** - *(optional)* adapter creation args (dict), forwarded to cursor creation by default.
      declarations to the python classes which aiosparql should use when marshaling SPARQL results.
    - **loader_cls** - *(optional)* Custom constructor for `QueryLoader` extensions.
    - **queries_cls** - *(optional)* Custom constructor for `Queries` extensions.
    - **ext** - *(optional)* allowed file extensions for query files, default is `(".rq",)`.
    - **encoding** - *(optional)* encoding for reading files.

    **Returns:** `Queries`

    Usage:

    .. code-block:: python

      queries = aiosparql.from_path("./sparql", "psycopg2")
      queries = aiosparql.from_path("./sparql", MyDBAdapter)
    """
    path = Path(sparql_path)

    if not path.exists():
        raise SPARQLLoadException(f"File does not exist: {path}")

    adapter = _make_driver_adapter(driver_adapter, *args, **kwargs)
    query_loader = loader_cls(adapter, record_classes, attribute=attribute)

    if path.is_file():
        query_data = query_loader.load_query_data_from_file(path, encoding=encoding)
        return queries_cls(adapter, kwargs_only=kwargs_only).load_from_list(query_data)
    elif path.is_dir():
        query_data_tree = query_loader.load_query_data_from_dir_path(
            path, ext=ext, encoding=encoding
        )
        return queries_cls(adapter, kwargs_only=kwargs_only).load_from_tree(
            query_data_tree
        )
    else:  # pragma: no cover
        raise SPARQLLoadException(
            f"The sparql_path must be a directory or file, got {sparql_path}"
        )
