python-hl7 - Easy HL7 v2.x Parsing
==================================

python-hl7 is a simple library for parsing messages of Health Level 7
(HL7) version 2.x into Python objects.  python-hl7 includes a simple
client that can send HL7 messages to a Minimal Lower Level Protocol (MLLP)
server (:ref:`mllp_send <mllp-send>`).

HL7 is a communication protocol and message format for 
health care data. It is the de-facto standard for transmitting data
between clinical information systems and between clinical devices.
The version 2.x series, which is often is a pipe delimited format
is currently the most widely accepted version of HL7 (version 3.0
is an XML-based format).

python-hl7 currently only parses HL7 version 2.x messages into
an easy to access data structure. The current implementation
does not completely follow the HL7 specification, but is good enough
to parse the most commonly seen HL7 messages. The library could 
potentially evolve into being fully complainant with the spec.
The library could eventually also contain the ability to create
HL7 v2.x messages.

python-hl7 parses HL7 into a series of wrapped :py:class:`hl7.Container` objects.
The there are specific subclasses of :py:class:`hl7.Container` depending on
the part of the HL7 message. The :py:class:`hl7.Container` message itself
is a subclass of a Python list, thus we can easily access the
HL7 message as an n-dimensional list. Specifically, the subclasses of
:py:class:`hl7.Container`, in order, are :py:class:`hl7.Message`, 
:py:class:`hl7.Segment`, and :py:class:`hl7.Field`.
Eventually additional containers will be added to fully support
the HL7 specification.

Usage
-----

As an example, let's create a HL7 message:

.. doctest::

    >>> message = 'MSH|^~\&|GHH LAB|ELAB-3|GHH OE|BLDG4|200202150930||ORU^R01|CNTRL-3456|P|2.4\r'
    >>> message += 'PID|||555-44-4444||EVERYWOMAN^EVE^E^^^^L|JONES|196203520|F|||153 FERNWOOD DR.^^STATESVILLE^OH^35292||(206)3345232|(206)752-121||||AC555444444||67-A4335^OH^20030520\r'
    >>> message += 'OBR|1|845439^GHH OE|1045813^GHH LAB|1554-5^GLUCOSE|||200202150730||||||||555-55-5555^PRIMARY^PATRICIA P^^^^MD^^LEVEL SEVEN HEALTHCARE, INC.|||||||||F||||||444-44-4444^HIPPOCRATES^HOWARD H^^^^MD\r'
    >>> message += 'OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F'

We call the :py:func:`hl7.parse` command with string message:

.. doctest::

    >>> import hl7
    >>> h = hl7.parse(message)

We get a :py:class:`hl7.Message` object, wrapping a series of 
:py:class:`hl7.Segment` objects:

.. doctest::

    >>> type(h)
    <class 'hl7.Message'>

We can always get the HL7 message back:

.. doctest::

    >>> unicode(h) == message
    True

Interestingly, :py:class:`hl7.Message` can be accessed as a list:

.. doctest::

    >>> isinstance(h, list)
    True

There were 4 segments (MSH, PID, OBR, OBX):

.. doctest::

    >>> len(h)
    4

We can extract the :py:class:`hl7.Segment` from the 
:py:class:`hl7.Message` instance:

.. doctest::

    >>> h[3]
    [[u'OBX'], [u'1'], [u'SN'], [u'1554-5', u'GLUCOSE', u'POST 12H CFST:MCNC:PT:SER/PLAS:QN'], [u''], [u'', u'182'], [u'mg/dl'], [u'70_105'], [u'H'], [u''], [u''], [u'F']]

We can easily reconstitute this segment as HL7, using the
appropriate separators:

.. doctest::

    >>> unicode(h[3])
    u'OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F'

We can extract individual elements of the message:

.. doctest::

    >>> h[3][3][1]
    u'GLUCOSE'
    >>> h[3][5][1]
    u'182'

We can look up segments by the segment identifier, either via
:py:meth:`hl7.Message.segments` or via the traditional dictionary
syntax:

.. doctest::

    >>> h.segments('OBX')[0][3][1]
    u'GLUCOSE'
    >>> h['OBX'][0][3][1]
    u'GLUCOSE'

Since many many types of segments only have a single instance in a message
(e.g. PID or MSH), :py:meth:`hl7.Message.segment` provides a convienance
wrapper around :py:meth:`hl7.Message.segments` that returns the first matching
:py:class:`hl7.Segment`:

.. doctest::

    >>> h.segment('PID')[3][0]
    u'555-44-4444'


MLLP network client - ``mllp_send``
-----------------------------------

python-hl7 features a simple network client, ``mllp_send``, which reads HL7
messages from a file or ``sys.stdin`` and posts them to an MLLP server.
``mllp_send`` is a command-line wrapper around 
:py:class:`hl7.client.MLLPClient`.  ``mllp_send`` is a useful tool for
testing HL7 interfaces or resending logged messages::

    mllp_send --file sample.hl7 --port 6661 mirth.example.com

See :doc:`mllp_send` for examples and usage instructions.

Contents
--------

.. toctree::
   :maxdepth: 1

   api
   mllp_send
   contribute
   changelog
   authors
   license

Install
-------

python-hl7 is available on `PyPi <http://pypi.python.org/pypi/hl7>`_ 
via ``pip`` or ``easy_install``::

    pip install -U hl7

For recent versions of Debian and Ubuntu, the *python-hl7* package is 
available::

    sudo apt-get install python-hl7

Links
-----

* Documentation: http://python-hl7.readthedocs.org
* Source Code: http://github.com/johnpaulett/python-hl7
* PyPi: http://pypi.python.org/pypi/hl7

HL7 References:

* `Health Level 7 - Wikipedia <http://en.wikipedia.org/wiki/HL7>`_
* `nule.org's Introduction to HL7 <http://nule.org/wp/?page_id=99>`_
* `hl7.org <http://www.hl7.org/>`_
* `OpenMRS's HL7 documentation <http://openmrs.org/wiki/HL7>`_
* `Transport Specification: MLLP <http://www.hl7.org/v3ballot/html/infrastructure/transport/transport-mllp.html>`_
