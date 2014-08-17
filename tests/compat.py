import sys

# TODO Remove once 2.6 compat is removed
if sys.version_info < (3, 0):
    import unittest2 as unittest
else:
    import unittest

try:
    # Added in Python 3.3
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock


__all__ = ['unittest', 'patch', 'Mock']
