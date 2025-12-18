from SPARQLWrapper import SPARQLWrapper, JSON

import pytest


@pytest.fixture
def sparql_wrapper():
    sparql = SPARQLWrapper(
        "http://vocabs.ardc.edu.au/repository/api/sparql/"
        "csiro_international-chronostratigraphic-chart_geologic-time-scale-2020"
    )
    sparql.setReturnFormat(JSON)
    return sparql
