from pathlib import Path
from typing import NamedTuple, Iterable
from datetime import date
import dataclasses
import asyncio
import re
import pytest

import ouisparql

from conf_sparql_wrapper import sparql_wrapper


def test_query(sparql_wrapper):
    sparql_wrapper.setQuery("""
    PREFIX gts: <http://resource.geosciml.org/ontology/timescale/gts#>

    SELECT *
    WHERE {
        ?a a gts:Age .
    }
    ORDER BY ?a
    LIMIT 3
    """)

    try:
        ret = sparql_wrapper.queryAndConvert()

        for r in ret["results"]["bindings"]:
            print(r)
    except Exception as e:
        print(e)


def test_query_loader(sparql_wrapper):
    queries = ouisparql.from_path("tests/sparql/queries.rq", "sparql_wrapper")
    print(queries.available_queries)
    ret = queries.get_all_predicate(sparql_wrapper)
    for r in ret:
        print(r)


"""
def test_query_loader_with_variable(sparql_wrapper):
    queries = ouisparql.from_path("tests/sparql/queries.rq", "sparql_wrapper")
    ret = queries.get_by_predicate(sparql_wrapper, age="gts:Age")
    for r in ret:
        print(r)
"""


def test_parameter_replace(sparql_wrapper):
    queries = ouisparql.from_path("tests/sparql/queries.rq", "sparql_wrapper")
    ret = queries.get_subject_by_predicate(sparql_wrapper, predicate="rdf:type")
    for r in ret:
        print(r)
