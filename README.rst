pylint-report
==============

Generates an html report summarizing the results of `pylint <https://www.pylint.org/>`_.

Installation
-------------

.. code-block:: shell

   pip install pylint-report

How to use
-----------

Place the following in your ``.pylintrc`` (or specify the ``--load-plugins`` and ``--output-format`` flags)

.. code-block:: shell

   [MASTER]
   load-plugins=pylint_report.pylint_report

   [REPORTS]
   output-format=pylint_report.pylint_report.CustomJsonReporter

* A two-step approach:

  + ``pylint path/to/code > report.json``: generate a (custom) ``json`` file using ``pylint``

  + ``pylint_report.py report.json --html-file report.html``: generate html report

* Or alternatively ``pylint path/to/code | pylint_report.py > report.html``

* ``cat report.json | pylint_report.py -s`` returns only the pylint score

* To use without installation specify ``export PYTHONPATH="/path/to/pylint-report"``.

Based on
---------

* https://github.com/Exirel/pylint-json2html
* https://stackoverflow.com/a/57511754
