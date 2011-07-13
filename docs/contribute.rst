Contributing
============

The source code is available at http://github.com/johnpaulett/python-hl7

The test suite uses `nose <http://pypi.python.org/pypi/nose>`_::

    $ nosetest
    ...............
    ----------------------------------------------------------------------
    Ran 15 tests in 0.010s
    
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
