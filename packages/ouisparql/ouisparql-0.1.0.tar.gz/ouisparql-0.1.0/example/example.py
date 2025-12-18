import argparse
import sparqlite3
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import ouisparql
from ouisparql.adapters.sparqlwrapper import SPARQLWrapperAdapter

dir_path = Path(__file__).parent
sparql_path = dir_path / "sparql"
# db_path = dir_path / "exampleblog.db"
queries = ouisparql.from_path(dir_path / "sparql", SPARQLWrapperAdapter)


def get_conn():
    pass


def createdb():
    pass


def deletedb():
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
