Contributing
============

First, thank you for considering to make a contribution to this project.
Spending your valuable time helping make this project better is deeply appreciated.
All kinds of contributions are helpful and welcome.

-  Report issues `<https://gitlab.com/sortion/ouisparql/-/issues>`__
-  Review or make your own pull requests `<https://gitlab.com/sortion/ouisparql/-/merge_requests>`__
-  Write documentation `<https://gitlab.com/sortion/ouisparql/-/tree/main/docs/source>`__

Whether you have an idea for a feature improvement or have found a troubling bug, thank you for being here.


Packaging & Distribution
------------------------

This ouisparql repository uses the Python standard packaging tools.
Read about them in more detail at the following links.

-  `Python Packaging User Guide <https://packaging.python.org/>`__
-  `PyPA - Packaging & Distributing projects <https://packaging.python.org/guides/distributing-packages-using-setuptools/>`__
-  `setuptools <https://setuptools.readthedocs.io/en/latest/index.html>`__
-  `build <https://pypa-build.readthedocs.io/en/stable/>`__
-  `twine <https://twine.readthedocs.io/en/latest/#configuration>`__

Development Setup
-----------------

1. Create a virtual environment

.. code:: sh

    # get the project sources
    git clone git@gitlab.com:sortion/ouisparql.git
    cd ouisparql
    # create a venv manually
    python -m venv .venv/ouisparql
    source .venv/ouisparql/bin/activate
    pip install --upgrade pip

All subsequent steps will assume you are using python within your activated virtual environment.

1. Install the development dependencies

As a development library, ouisparql is expected to work with all supported
versions of Python, and many drivers.
The bare minimum of version pinning is declared in the dependencies.

.. code:: sh

    # development tools
    pip install .[dev]

1. Run tests

.. code:: sh

    pytest

Alternatively, there is a convenient ``Makefile`` to automate the above tasks:

.. code:: sh

    make venv.dev  # install dev virtual environment
    source .venv/ouisparql/bin/activate
    make check  # run all checks: pytest, flake8, coverage…


Dependency Management
---------------------

There is no dependency for using ``ouisparql`` other than installing your driver of choice.
You will most probably need to install ``SPARQLWrapper``.
