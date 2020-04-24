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

  + optionally one could add a figure: ``pylint path/to/code | pylint_report.py --score-history-fig score_history.png > report.html``

  + the figure can be generated from log files using: ``pylint_report.py --score-history-dir logs --score-history-fig score_history.png``

    For more information regarding the format of the logs see ``pylint_report.get_score_history``.

* ``cat report.json | pylint_report.py -s`` returns only the pylint score

* To use without installation specify ``export PYTHONPATH="/path/to/pylint-report"``.

Based on
---------

* https://github.com/Exirel/pylint-json2html
* https://stackoverflow.com/a/57511754
