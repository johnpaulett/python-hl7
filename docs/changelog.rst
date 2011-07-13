Change Log
==========

0.2.0
-----

* Converted ``hl7.segment`` and ``hl7.segments`` into methods on 
  :py:class:`hl7.Message`.
* Support dict-syntax for getting Segments from a Message (e.g. ``message['OBX']``)
* Use unicode throughout python-hl7 since the HL7 spec allows non-ASCII characters.
  It is up to the caller of `py:func:`hl7.parse` to convert non-ASCII messages
  into unicode.
* Refactored from single hl7.py file into the hl7 module.
* Added Sphinx `documentation <http://python-hl7.readthedocs.org>`_.
  Moved project to `github <http://github.com/johnpaulett/python-hl7>`_.
