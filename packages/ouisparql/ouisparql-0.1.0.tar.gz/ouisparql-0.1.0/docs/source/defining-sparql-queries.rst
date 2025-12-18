Defining SPARQL Queries
=======================

Query Names
-----------

Name definitions are how ouisparql determines the name of the methods that SQL
code blocks are accessible by.
A query name is defined by a ouisparql comment of the form ``"# name: "``.
As a readability convenience, dash characters (``-``) in the name are turned
into underlines (``_``).

Query Comments
--------------

.. literalinclude:: ../../example/species/sparql/queries.rq
    :language: sparql
    :lines: 1-12

Any other SPARQL comments you make between the name definition and your code will
be used as the python documentation string for the generated method.
You can use ``help()`` in the Python REPL to view these comments while using python.

..
   FIXME method parameters are not shown…

.. code:: pycon

    Python 3 … on Linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import ouisparql
    >>> queries = ouisparql.from_path("queries.rq", "sparql_wrapper")
    >>> help(queries.get_all_mosquitoes)
    Help on method get_all_mosquitoes in module ouisparql.queries:

    get_all_mosquitoes(conn, *args, **kwargs) method of ouisparql.queries.Queries instance
        Mosquito species
        ----
        Species of mosquitoes
        added 2017-06
        source: Wikidata SPARQL query example


Named Parameters
----------------

Named parameters ``:param`` are accepted and taken
from Python named parameters passed to the query.
In addition, simple attributes can be referenced with the ``.``-syntax.

.. literalinclude:: ../../tests/sparql/queries.rq
   :language: sparql
   :lines: 12-22

Then the generated function expects one named parameters, (here named ``predicate``):

.. code:: python

    res = queries.get_by_predicate(predicate="rdf:type")

Parameter Declarations
----------------------

Query parameter names may be declared in parentheses just after the method name.

.. literalinclude:: ../../tests/sparql/queries.rq
   :language: sparql
   :lines: 23-32 


When declared they are checked, raising errors when parameters are unused or undeclared.
