Getting Started
===============

Philosophy
----------



Loading Queries
---------------

This section goes over the three ways to make SQL queries available for execution in python.
You'll learn the basics of defining queries so aiosql can find them and turn them into methods
on a ``Queries`` object.
For more details reference the :doc:`defining-sparql-queries` documentation.

From a SPARQL File
~~~~~~~~~~~~~~~

SPARQL can be loaded by providing a path to a ``.rq`` file.
Below is a *queries.rq* file that defines two queries.

.. code:: sparql

  # name: get_all_mosquitoes
  # Species of mosquitoes
  # source: Wikidata SPARQL query examples
  SELECT ?item ?taxonname WHERE {
    ?item wdt:P31 wd:Q16521;
      wdt:P105 wd:Q7432;
      (wdt:P171*) wd:Q7367;
      wdt:P225 ?taxonname.
  }

  # TODO: add a named parameter example.

Notice the ``# name: <name_of_method>`` comments.
.. and the ``:username`` substitution variable.
The comments that start with ``# name:`` are the magic of ouisparql.
They are used by ```ouisparql.from_path`` <./api.md#ouisparqlfrom_path>`__ to parse the file
into separate methods accessible by the name.
The ``ouisparql.from_path`` function takes a path to a SPARQL file or directory
and the name of the database driver intended for use with the methods.

.. code:: python

    queries = ouisparql.from_path("queries.rq", "sparql_wrapper")

In the case of *queries.rq* we expect the following two methods to be available.

.. code:: python

    def get_all_mosquitoes(self, conn) -> Generator[Any]:
        pass



From an SPARQL String
~~~~~~~~~~~~~~~~~~

SPARQL can be loaded from a string as well.
The result below is the same as the first example above that loads from a SPARQL file.

.. code:: python

  sparql_str = """
      # name: get_all_mosquitoes
      # Species of mosquitoes
      # source: Wikidata SPARQL query examples
      SELECT ?item ?taxonname WHERE {
          ?item wdt:P31 wd:Q16521;
          wdt:P105 wd:Q7432;
          (wdt:P171*) wd:Q7367;
          wdt:P225 ?taxonname.
       }
       """
  queries = ouisparql.from_str(sparql_str, "sparql_wrapper")

The ``Queries`` object here will have two methods:

.. code:: python

    queries.get_all_mosquitoes(conn)

.. queries.get_user_blogs(conn, username="johndoe")

..
  From a Directory of SQL Files
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Loading a directory of SQL files loads all of the queries defined in those files into a single object.
  The ``example/sparql`` directory below contains three ``.rq`` files and can be loaded using
  ``ouisparql.from_path`` `<./api.md#ouisparqlfrom_path>`__.

  ::

      example/sparql

  .. code:: python

      queries = aiosql.from_path("example/sql", "sqlite3")

  The resulting ``queries`` object will have a mixture of methods from all the files.

  Subdirectories
  ^^^^^^^^^^^^^^

  Introducing subdirectories allows namespacing queries.
  This provides a way to further organize and group queries conceptually.
  For instance, you could define blog queries separate from user queries access them on distinct
  properties of the queries object.

  Assume the *mosquitoes.rq* and *users.sql* files both contain a ``# name: get_all_mosquitoes`` query.



      example/sql/
              ├── blogs/
              │   └── blogs.sql
              ├── create_schema.sql
              └── users/
                  └── users.sql

  .. code:: python

      queries = aiosql.from_path("example/sql", "sqlite3")

  The ``Queries`` object has two nested ``get_all`` methods accessible on attributes ``.blogs`` and ``.users``.
  The attributes reflect the names of the subdirectories.

  .. code:: python

      queries.blogs.get_all(conn)
      queries.users.get_all(conn)

Calling Query Methods
---------------------

Connections
~~~~~~~~~~~

The connection or ``conn`` is always the first argument to an ``ouisparql`` method.
The ``conn`` is a ``SPARQLWrapper`` instance  that your ouisparql method can use for query the SPARQL it contains.
Controlling connections outside of ouisparql queries means you can call multiple queries and control them under one transaction,
or otherwise set connection level properties that affect driver behavior.

.. note::

    For more see: :doc:`advanced-topics`.
