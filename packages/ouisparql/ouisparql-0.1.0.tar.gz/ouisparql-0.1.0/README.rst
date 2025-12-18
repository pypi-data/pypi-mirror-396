ouisparql - Simple SPARQL in Python
===================================

`SPARQL <https://en.wikipedia.org/wiki/SPARQL>`__ is code.
Write it, version control it, comment it, and run it using files.
Writing your SPARQL code in Python programs as strings doesn't allow you to easily
reuse them in SPARQL GUIs or CLI tools.
With `ouisparql` you can organize your SPARQL statements in *.sparql* files, load them
into your python application as methods to call without losing the ability to
use them as you would any other SPARQL file.


This module is an implementation of
`Kris Jenkins' yesql <https://github.com/krisajenkins/yesql>`__
`Clojure <https://clojure.org/>`__ library to the
`Python <https://www.python.org/>`__
`ecosystem <https://pypi.org/>`__, adapted from `aiosql <https://nackjicholson.github.io/aiosql/>`__ for SPARQL.

Badges
------
..
  ..
     NOTE :target: is needed so that github renders badges on a line.
  .. image:: https://github.com/nackjicholson/aiosql/actions/workflows/aiosql-package.yml/badge.svg?branch=main&style=flat
     :alt: Build status
     :target: https://github.com/nackjicholson/aiosql/actions/
  ..
     NOTE hardcoded, this is maintained manually.
  .. image:: https://img.shields.io/badge/coverage-100%25-success
     :alt: Code Coverage
     :target: https://github.com/nackjicholson/aiosql/actions/
  ..
     NOTE all tests
     .. image:: https://img.shields.io/badge/tests-247%20✓-success
     :alt: Tests
     :target: https://github.com/nackjicholson/aiosql/actions/
  .. image:: https://img.shields.io/github/issues/nackjicholson/aiosql?style=flat
     :alt: Issues
     :target: https://github.com/nackjicholson/aiosql/issues/
  .. image:: https://img.shields.io/github/contributors/nackjicholson/aiosql
     :alt: Contributors
     :target: https://github.com/nackjicholson/aiosql/graphs/contributors
  .. image:: https://img.shields.io/pypi/dm/aiosql?style=flat
     :alt: Pypi Downloads
     :target: https://pypistats.org/packages/aiosql
  .. image:: https://img.shields.io/github/stars/nackjicholson/aiosql?style=flat&label=Star
     :alt: Stars
     :target: https://github.com/nackjicholson/aiosql/stargazers
  .. image:: https://img.shields.io/pypi/v/aiosql
     :alt: Version
     :target: https://pypi.org/project/aiosql/
  .. image:: https://img.shields.io/github/languages/code-size/nackjicholson/aiosql?style=flat
     :alt: Code Size
     :target: https://github.com/nackjicholson/aiosql/
  .. image:: https://img.shields.io/badge/databases-6-informational
     :alt: Databases
     :target: https://github.com/nackjicholson/aiosql/
  .. image:: https://img.shields.io/badge/drivers-15-informational
     :alt: Drivers
     :target: https://github.com/nackjicholson/aiosql/
  .. image:: https://img.shields.io/github/languages/count/nackjicholson/aiosql?style=flat
     :alt: Language Count
     :target: https://en.wikipedia.org/wiki/Programming_language
  .. image:: https://img.shields.io/github/languages/top/nackjicholson/aiosql?style=flat
     :alt: Top Language
     :target: https://en.wikipedia.org/wiki/Python_(programming_language)
  .. image:: https://img.shields.io/pypi/pyversions/ouisparql?style=flat
     :alt: Python Versions
     :target: https://www.python.org/
  ..
     NOTE some non-sense badge about badges:-)
  .. image:: https://img.shields.io/badge/badges-16-informational
     :alt: Badges
     :target: https://shields.io/
  .. image:: https://img.shields.io/pypi/l/aiosql?style=flat
     :alt: BSD 2-Clause License
     :target: https://opensource.org/licenses/BSD-2-Clause


Usage
-----

Install from `pypi <https://pypi.org/project/ouisparql>`__, for instance by running ``pip install ouisparql``.

Install with pip from gitlab:

.. code:: bash

  pip install  git+https://gitlab.com/sortion/ouisparql.git@main

Then write parametric SPARQL queries in a file and execute it from Python methods,
e.g., this *predicates.sparql* file:

.. code:: sparql

    # name: get_predicates()
    # Get the first two predicates in the database
    SELECT DISTINCT ?predicate
    WHERE {
          ?subject ?predicate ?object .
    }

    # name: get_subject_by_predicate(predicate)
    # Get the first two subjects from a given predicate using a named parameter
    SELECT DISTINCT ?subject
    WHERE {
          ?subject :predicate ?object .
    }

This example has an imaginary SPARQL endpoint with RDF triplets.
It displays all predicates in the first example, and all subjects associated with a given predicate.

OuiSPARQL main feature is to be able to load queries from a SPARQL file and call them by name
in python code.
Query parameter declarations (e.g., ``(predicate)``) are optional, and enforced
when provided.

You can use ``ouisparql`` to load the queries in this file for use in your Python
application:

.. code:: python

    import ouisparql
    from SPARQLWrapper import SPARLQWrapper
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent="OuiSPARQL documentation")
    queries = ouisparql.from_path("queries.rq", "sparql_wrapper")
    queries.get_all_predicate()
    queries.get_subjects_by_predicate(predicate)



Why you might want to use this
------------------------------

* You think SPARQL is pretty good, and writing SPARQL is an important part of your applications.
* You don't want to write your SPARQL in strings intermixed with your python code.
* You want to be able to reuse your SPARQL in other contexts,
  e.g., loading it into a SPARQL endpoint or other tools.

Why you might NOT want to use this
----------------------------------

* You aren't comfortable writing SPARQL code.
* Dynamically loaded objects built at runtime really bother you.
