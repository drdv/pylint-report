pylint-report
==============

Generates an HTML report summarizing the results of `pylint <https://www.pylint.org/>`_.

Installation
-------------

The recommended way to install ``pylint-report`` is using

.. code-block:: bash

   pip install pylint-report

or, for a development version (with all optional dependencies):

.. code-block:: bash

   pip install pylint-report[dev]

Quickstart
===========

Place the following in ``.pylintrc``

.. code-block:: shell

   [MASTER]
   load-plugins=pylint_report

   [REPORTS]
   output-format=pylint_report.CustomJsonReporter

or place the following in ``pyproject.toml``

.. code-block:: toml

   [tool.pylint.MASTER]
   load-plugins = "pylint_report"

   [tool.pylint.REPORTS]
   output-format = "pylint_report.CustomJsonReporter"

or manually pass the ``--load-plugins`` and ``--output-format`` flags.

* A two-step approach:

  + ``pylint path/to/code > report.json``: generate a (custom) ``json`` file using ``pylint``

  + ``pylint_report.py report.json -o report.html``: generate html report

* Or alternatively ``pylint path/to/code | pylint_report.py > report.html``

Based on
---------

* https://github.com/Exirel/pylint-json2html
* https://stackoverflow.com/a/57511754
