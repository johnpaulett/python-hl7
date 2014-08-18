"""Python 2/3 Compatibility Helper

Inspired by:

* https://docs.djangoproject.com/en/dev/topics/python3/
* http://lucumr.pocoo.org/2011/1/22/forwards-compatible-python/
* http://python-future.org/index.html
* http://docs.python.org/3.3/howto/pyporting.html

"""
import six


def python_2_unicode_compatible(cls):
    """
    Class decorator that provides appropriate Python 2 __unicode__ and __str__
    based upon Python 3' __str__.
    """
    if six.PY2:
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda self: self.__unicode__().encode('utf-8')
    return cls
