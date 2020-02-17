Contributing
============

The source code is available at http://github.com/johnpaulett/python-hl7

Please fork and issue pull requests.  Generally any changes, bug fixes, or
new features should be accompanied by corresponding tests in our test
suite.


Testing
--------

The test suite is located in :file:`tests/` and can be run several ways.

It is recommended to run the full `tox <http://tox.testrun.org/>`_ suite so
that all supported Python versions are tested and the documentation is built
and tested.  We provide a :file:`Makefile` to create a virtualenv, install tox,
and run tox::

    $ make tests
      py27: commands succeeded
      py26: commands succeeded
      docs: commands succeeded
      congratulations :)

To run the test suite with a specific python interpreter::

    python setup.py test

To documentation is built by tox, but you can manually build via::

   $ make docs
   ...
   Doctest summary
   ===============
      23 tests
       0 failures in tests
       0 failures in setup code
   ...


Formatting
----------

python-hl7 has converted to use `black <https://black.readthedocs.io/en/stable/>`
to enforce a coding style.  To automatically format using black and isort::

    $ make format

It is also recommended to run the flake8 checks for PEP8 and PyFlake
violations.  Commits should be free of warnings::

    $ make lint
