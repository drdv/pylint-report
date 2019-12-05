pylint-report
==============

Generates an html report summarizing the results of `pylint <https://www.pylint.org/>`_.

Installation
-------------

* Directly install from the github repository

  .. code-block:: shell

     pip install -e git+git://github.com/drdv/pylint-report.git#egg=pylint-report

* Install using ``.requirements.txt`` file

  .. code-block:: shell

     pip install -r .requirements.txt

  Where your ``.requirements.txt`` file contains the following line

  .. code-block:: shell

     -e git+git://github.com/drdv/pylint-report.git#egg=pylint-report

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

  + ``./pylint_report.pylint_report report.json --html-file report.html``: generate html report

* Or alternatively ``pylint path/to/code | ./pylint_report.pylint_report > report.html``

* ``cat report.json | ./pylint_report.pylint_report -s`` returns only the pylint score

* Using ``pylint-report`` without installation requires specifying ``export PYTHONPATH="/path/to/pylint_report"``.

Based on
---------

* https://github.com/Exirel/pylint-json2html
* https://stackoverflow.com/a/57511754
