from contextlib import contextmanager
from .generic import GenericAdapter


class SPARQLWrapperAdapter(GenericAdapter):
    """
    OuiSPARQL Adapter for SPARQLWrapper.
    """

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def replace_parameters(self, sparql: str, parameters: dict[str, str]) -> str:
        for key, val in parameters.items():
            sparql = sparql.replace(f":{key}", val)
        return sparql

    def select(self, conn, query_name: str, sparql: str, parameters, record_class=None):
        """Handle a relation-returning SELECT (no suffix)."""
        print(sparql)
        sparql = self.replace_parameters(sparql, parameters)
        print(sparql)
        conn.setQuery(sparql)
        ret = conn.queryAndConvert()
        for r in ret["results"]["bindings"]:
            yield r

    def select_one(self, conn, query_name, sparql, parameters, record_class=None):
        """Handle a tuple-returning (one row) SELECT (``^`` suffix).

        Return None if empty."""
        raise NotImplementedError()
        cur = self._cursor(conn)
        try:
            cur.execute(sparql, parameters)
            result = cur.fetchone()
            if result is not None and record_class is not None:
                column_names = [c[0] for c in cur.description]
                # this fails if result is not a list or tuple
                result = record_class(**dict(zip(column_names, result)))
        finally:
            cur.close()
        return result

    def select_value(self, conn, query_name, sparql, parameters):
        """Handle a scalar-returning (one value) SELECT (``$`` suffix).

        Return None if empty."""
        raise NotImplementedError()
        cur = self._cursor(conn)
        try:
            cur.execute(sparql, parameters)
            result = cur.fetchone()
            if result:
                if isinstance(result, (list, tuple)):
                    return result[0]
                elif isinstance(result, dict):  # pragma: no cover
                    return next(iter(result.values()))
                else:  # pragma: no cover
                    raise Exception(f"unexpected value type: {type(result)}")
            else:
                return None
        finally:
            cur.close()

    @contextmanager
    def select_cursor(self, conn, query_name, sparql, parameters):
        """Return the raw cursor after a SELECT exec."""
        conn.setQuery(sparql)
        ret = conn.queryAndConvert()
        for r in ret["results"]["bindings"]:
            yield r

    def insert_update_delete(self, conn, query_name, sparql, parameters):
        """Handle affected row counts (INSERT UPDATE DELETE) (``!`` suffix)."""
        raise NotImplementedError()
        cur = self._cursor(conn)
        cur.execute(sparql, parameters)
        rc = cur.rowcount if hasattr(cur, "rowcount") else -1
        cur.close()
        return rc

    def insert_update_delete_many(self, conn, query_name, sparql, parameters):
        """Handle affected row counts (INSERT UPDATE DELETE) (``*!`` suffix)."""
        raise NotImplementedError()
        cur = self._cursor(conn)
        cur.executemany(sparql, parameters)
        rc = cur.rowcount if hasattr(cur, "rowcount") else -1
        cur.close()
        return rc

    def execute_script(self, conn, sparql):
        """Handle an SPARQL script (``#`` suffix)."""
        raise NotImplementedError()
        cur = self._cursor(conn)
        cur.execute(sparql)
        msg = cur.statusmessage if hasattr(cur, "statusmessage") else "DONE"
        cur.close()
        return msg
