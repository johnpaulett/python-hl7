Change Log
==========

0.3.2 - unreleased
------------------

* new mechanism to address message parts via a symbolic accessor name
* Message (and Message.segments), Field, Repetition and Component can be
  accessed using 1-based indices by using them as a callable.

0.3.1 - unreleased
------------------

Non-backward compatible changes:

* Changed the numbering of fields in the MSH segment. This breaks older code.
* Parse all the elements of the message (i.e. down to sub-component). The
  inclusion of repetitions will break older code.

Others:

* implemented a basic escaping mechanism
* new constant 'NULL' which maps to '""'
* new isfile() / splitfile() functions to identify file (FHS/FTS wrapped messages)

0.3.0 - unreleased
------------------

* Added Python 3 support
* :py:func:`hl7.parse` can now decode byte strings, using the ``encoding``
  parameter. :py:class:`hl7.client.MLLPClient` can now encode unicode input
  using the ``encoding`` parameter.

0.2.5 - 2012-03-14
------------------

* Do not senselessly try to convert to unicode in mllp_send. Allows files to
  contain other encodings.

0.2.4 - 2012-02-21
------------------

* ``mllp_send --version`` prints version number
* ``mllp_send --loose`` algorithm modified to allow multiple messages per file.
  The algorithm now splits messages based upon the presumed start of a message,
  which must start with ``MSH|^~\&|``

0.2.3 - 2012-01-17
------------------

* ``mllp_send --loose`` accepts & converts Unix newlines in addition to
  Windows newlines

0.2.2 - 2011-12-17
------------------

* :ref:`mllp_send <mllp-send>` now takes the ``--loose`` options, which allows
  sending HL7 messages that may not exactly meet the standard (Windows newlines
  separating segments instead of carriage returns).

0.2.1 - 2011-08-30
------------------

* Added MLLP client (:py:class:`hl7.client.MLLPClient`) and command line tool,
  :ref:`mllp_send <mllp-send>`.

0.2.0 - 2011-06-12
------------------

* Converted ``hl7.segment`` and ``hl7.segments`` into methods on 
  :py:class:`hl7.Message`.
* Support dict-syntax for getting Segments from a Message (e.g. ``message['OBX']``)
* Use unicode throughout python-hl7 since the HL7 spec allows non-ASCII characters.
  It is up to the caller of :py:func:`hl7.parse` to convert non-ASCII messages
  into unicode.
* Refactored from single hl7.py file into the hl7 module.
* Added Sphinx `documentation <http://python-hl7.readthedocs.org>`_.
  Moved project to `github <http://github.com/johnpaulett/python-hl7>`_.

0.1.1 - 2009-06-27
------------------

* Apply Python 3 trove classifier

0.1.0 - 2009-03-13
------------------

* Support message-defined separation characters
* Message, Segment, Field classes

0.0.3 - 2009-01-09
------------------

* Initial release
