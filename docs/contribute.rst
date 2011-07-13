Contributing
============

The source code is available at http://github.com/johnpaulett/python-hl7

The test suite is located in :file:`tests/` and can be run via :file:`setup.py`::

    $ python setup.py test
    ...
    ----------------------------------------------------------------------
    Ran 17 tests in 0.005s

    OK

Make sure the documentation is still valid::

   $ pushd docs && make html && make doctest && popd
   ...
   Doctest summary
   ===============
      23 tests
       0 failures in tests
       0 failures in setup code
   ...
