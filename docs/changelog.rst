Changelog
=========

0.4.3 - March 2022
---------------------

* Dropped support for Python 3.5 & 3.6. Python 3.7 - 3.10 now supported.
* Ensure :py:func:`hl7.parse_hl7` allows legitimate occurrences of "MSH" inside
  the message contents

0.4.2 - February 2021
---------------------

* Added support for :py:class:`hl7.Batch` and :py:class:`hl7.File`, via
  :py:func:`hl7.parse_hl7` or the more specific :py:func:`hl7.parse_batch`
  and :py:func:`parse_file`.

Thanks `Joseph Wortmann <https://github.com/joseph-wortmann>`_!


0.4.1 - September 2020
----------------------

* Experimental asyncio-based HL7 MLLP support. :doc:`mllp`, via
  :py:func:`hl7.mllp.open_hl7_connection` and
  :py:func:`hl7.mllp.start_hl7_server`

Thanks `Joseph Wortmann <https://github.com/joseph-wortmann>`_!


.. _changelog-0-4-0:

0.4.0 - September 2020
----------------------

* Message now ends with trailing carriage return, to be consistent with Message
  Construction Rules (Section 2.6, v2.8). [`python-hl7#26 <https://github.com/johnpaulett/python-hl7/issues/26>`]
* Handle ASCII characters within :py:meth:`hl7.Message.escape` under Python 3.
* Don't escape MSH-2 so that the control characters are retrievable. [`python-hl7#27 <https://github.com/johnpaulett/python-hl7/issues/27>`]
* Add MSH-9.1.3 to create_ack.
* Dropped support for Python 2.7, 3.3, & 3.4. Python 3.5 - 3.8 now supported.
* Converted code style to use black.

Thanks `Lucas Kahlert <https://github.com/f3anaro>`_ &
`Joseph Wortmann <https://github.com/joseph-wortmann>`_!


0.3.5 - June 2020
-----------------
* Handle ASCII characters within :py:meth:`hl7.Message.escape` under Python 3.

Thanks `Lucas Kahlert <https://github.com/f3anaro>`_!


0.3.4 - June 2016
-----------------
* Fix bug under Python 3 when writing to stdout from `mllp_send`
* Publish as a Python wheel


0.3.3 - June 2015
-----------------
* Expose a Factory that allows control over the container subclasses created
  to construct a message
* Split up single module into more manageable submodules.

Thanks `Andrew Wason <https://github.com/rectalogic>`_!


0.3.2 - September 2014
----------------------
* New :py:func:`hl7.parse_datetime` for parsing HL7 DTM into python
  :py:class:`datetime.datetime`.


0.3.1 - August 2014
-------------------

* Allow HL7 ACK's to be generated from an existing Message via
  :py:meth:`hl7.Message.create_ack`

.. _changelog-0-3-0:

0.3.0 - August 2014
-------------------

.. warning::

  :ref:`0.3.0 <changelog-0-3-0>` breaks backwards compatibility by correcting
  the indexing of the MSH segment and the introducing improved parsing down to
  the repetition and sub-component level.


* Changed the numbering of fields in the MSH segment.
  **This breaks older code.**
* Parse all the elements of the message (i.e. down to sub-component). **The
  inclusion of repetitions will break older code.**
* Implemented a basic escaping mechanism
* New constant 'NULL' which maps to '""'
* New :py:func:`hl7.isfile` and  :py:func:`hl7.split_file` functions to
  identify file (FHS/FTS) wrapped messages
* New mechanism to address message parts via a :doc:`symbolic accessor name
  </accessors>`
* Message (and Message.segments), Field, Repetition and Component can be
  accessed using 1-based indices by using them as a callable.
* Added Python 3 support.  Python 2.6, 2.7, and 3.3 are officially supported.
* :py:func:`hl7.parse` can now decode byte strings, using the ``encoding``
  parameter. :py:class:`hl7.client.MLLPClient` can now encode unicode input
  using the ``encoding`` parameter. To support Python 3, unicode is now
  the primary string type used inside the library. bytestrings are only
  allowed at the edge of the library now, with ``hl7.parse`` and sending
  via ``hl7.client.MLLPClient``.  Refer to :ref:`unicode-vs-byte-strings`.
* Testing via tox and travis CI added.  See :doc:`contribute`.

A massive thanks to `Kevin Gill <https://github.com/kevingill1966>`_ and
`Emilien Klein <https://github.com/e2jk>`_ for the initial code submissions
to add the improved parsing, and to
`Andrew Wason <https://github.com/rectalogic>`_ for rebasing the initial pull
request and providing assistance in the transition.


0.2.5 - March 2012
------------------

* Do not senselessly try to convert to unicode in mllp_send. Allows files to
  contain other encodings.

0.2.4 - February 2012
---------------------

* ``mllp_send --version`` prints version number
* ``mllp_send --loose`` algorithm modified to allow multiple messages per file.
  The algorithm now splits messages based upon the presumed start of a message,
  which must start with ``MSH|^~\&|``

0.2.3 - January 2012
--------------------

* ``mllp_send --loose`` accepts & converts Unix newlines in addition to
  Windows newlines

0.2.2 - December 2011
---------------------

* :ref:`mllp_send <mllp-send>` now takes the ``--loose`` options, which allows
  sending HL7 messages that may not exactly meet the standard (Windows newlines
  separating segments instead of carriage returns).

0.2.1 - August 2011
-------------------

* Added MLLP client (:py:class:`hl7.client.MLLPClient`) and command line tool,
  :ref:`mllp_send <mllp-send>`.

0.2.0 - June 2011
-----------------

* Converted ``hl7.segment`` and ``hl7.segments`` into methods on 
  :py:class:`hl7.Message`.
* Support dict-syntax for getting Segments from a Message (e.g. ``message['OBX']``)
* Use unicode throughout python-hl7 since the HL7 spec allows non-ASCII characters.
  It is up to the caller of :py:func:`hl7.parse` to convert non-ASCII messages
  into unicode.
* Refactored from single hl7.py file into the hl7 module.
* Added Sphinx `documentation <http://python-hl7.readthedocs.org>`_.
  Moved project to `github <http://github.com/johnpaulett/python-hl7>`_.

0.1.1 - June 2009
-----------------

* Apply Python 3 trove classifier

0.1.0 - March 2009
------------------

* Support message-defined separation characters
* Message, Segment, Field classes

0.0.3 - January 2009
--------------------

* Initial release
