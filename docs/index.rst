python-hl7 - Easy HL7 v2.x Parsing
==================================

python-hl7 is a simple library for parsing messages of Health Level 7
(HL7) version 2.x into Python objects.  python-hl7 includes a simple
client that can send HL7 messages to a Minimal Lower Level Protocol (MLLP)
server (:ref:`mllp_send <mllp-send>`).

HL7 is a communication protocol and message format for
health care data. It is the de-facto standard for transmitting data
between clinical information systems and between clinical devices.
The version 2.x series, which is often in a pipe delimited format,
is currently the most widely accepted version of HL7 (there
is an alternative XML-based format).

python-hl7 currently only parses HL7 version 2.x messages into
an easy to access data structure. The library could eventually
also contain the ability to create HL7 v2.x messages.

python-hl7 parses HL7 into a series of wrapped :py:class:`hl7.Container` objects.
The there are specific subclasses of :py:class:`hl7.Container` depending on
the part of the HL7 message. The :py:class:`hl7.Container` message itself
is a subclass of a Python list, thus we can easily access the
HL7 message as an n-dimensional list. Specifically, the subclasses of
:py:class:`hl7.Container`, in order, are :py:class:`hl7.Message`,
:py:class:`hl7.Segment`, :py:class:`hl7.Field`, :py:class:`hl7.Repetition`.
and :py:class:`hl7.Component`.

python-hl7 includes experimental asyncio-based HL7 MLLP support in :doc:`mllp`,
which aims to replace `txHL7 <https://txhl7.readthedocs.io/>`_.


.. image::
   https://github.com/johnpaulett/python-hl7/workflows/Python%20package/badge.svg
   :target: https://github.com/johnpaulett/python-hl7/actions



Result Tree
-----------

HL7 Messages have a limited number of levels. The top level is a Message.
A Message is comprised of a number of Fields (:py:class:`hl7.Field`).
Fields can repeat (:py:class:`hl7.Repetition`). The content of a field
is either a primitive data type (such as a string) or a composite
data type comprised of one or more Components (:py:class:`hl7.Component`). Components
are in turn comprised of Sub-Components (primitive data types).

The result of parsing is accessed as a tree using python list conventions:

    ``Message[segment][field][repetition][component][sub-component]``

The result can also be accessed using HL7 1-based indexing conventions by treating
each element as a callable:

    ``Message(segment)(field)(repetition)(component)(sub-component)``


Usage
-----

As an example, let's create a HL7 message:

.. doctest::

    >>> message = 'MSH|^~\&|GHH LAB|ELAB-3|GHH OE|BLDG4|200202150930||ORU^R01|CNTRL-3456|P|2.4\r'
    >>> message += 'PID|||555-44-4444||EVERYWOMAN^EVE^E^^^^L|JONES|196203520|F|||153 FERNWOOD DR.^^STATESVILLE^OH^35292||(206)3345232|(206)752-121||||AC555444444||67-A4335^OH^20030520\r'
    >>> message += 'OBR|1|845439^GHH OE|1045813^GHH LAB|1554-5^GLUCOSE|||200202150730||||||||555-55-5555^PRIMARY^PATRICIA P^^^^MD^^LEVEL SEVEN HEALTHCARE, INC.|||||||||F||||||444-44-4444^HIPPOCRATES^HOWARD H^^^^MD\r'
    >>> message += 'OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F\r'

We call the :py:func:`hl7.parse` command with string message:

.. doctest::

    >>> import hl7
    >>> h = hl7.parse(message)

We get a :py:class:`hl7.Message` object, wrapping a series of
:py:class:`hl7.Segment` objects:

.. doctest::

    >>> type(h)
    <class 'hl7.containers.Message'>

We can always get the HL7 message back:

.. doctest::

    >>> str(h) == message
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
    [['OBX'], ['1'], ['SN'], [[['1554-5'], ['GLUCOSE'], ['POST 12H CFST:MCNC:PT:SER/PLAS:QN']]], [''], [[[''], ['182']]], ['mg/dl'], ['70_105'], ['H'], [''], [''], ['F']]
    >>> h[3] is h(4)
    True

Note that since the first element of the segment is the segment name,
segments are effectively 1-based in python as well (because the HL7 spec does
not count the segment name as part of the segment itself):

.. doctest::

    >>> h[3][0]
    ['OBX']
    >>> h[3][1]
    ['1']
    >>> h[3][2]
    ['SN']
    >>> h(4)(2)
    ['SN']

We can easily reconstitute this segment as HL7, using the
appropriate separators:

.. doctest::

    >>> str(h[3])
    'OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F'

We can extract individual elements of the message:

.. doctest::

    >>> h[3][3][0][1][0]
    'GLUCOSE'
    >>> h[3][3][0][1][0] is h(4)(3)(1)(2)(1)
    True
    >>> h[3][5][0][1][0]
    '182'
    >>> h[3][5][0][1][0] is h(4)(5)(1)(2)(1)
    True

We can look up segments by the segment identifier, either via
:py:meth:`hl7.Message.segments` or via the traditional dictionary
syntax:

.. doctest::

    >>> h.segments('OBX')[0][3][0][1][0]
    'GLUCOSE'
    >>> h['OBX'][0][3][0][1][0]
    'GLUCOSE'
    >>> h['OBX'][0][3][0][1][0] is h['OBX'](1)(3)(1)(2)(1)
    True

Since many many types of segments only have a single instance in a message
(e.g. PID or MSH), :py:meth:`hl7.Message.segment` provides a convenience
wrapper around :py:meth:`hl7.Message.segments` that returns the first matching
:py:class:`hl7.Segment`:

.. doctest::

    >>> h.segment('PID')[3][0]
    '555-44-4444'
    >>> h.segment('PID')[3][0] is h.segment('PID')(3)(1)
    True

The result of parsing contains up to 5 levels. The last level is a non-container
type.

.. doctest::

    >>> type(h)
    <class 'hl7.containers.Message'>

    >>> type(h[3])
    <class 'hl7.containers.Segment'>

    >>> type(h[3][3])
    <class 'hl7.containers.Field'>

    >>> type(h[3][3][0])
    <class 'hl7.containers.Repetition'>

    >>> type(h[3][3][0][1])
    <class 'hl7.containers.Component'>

    >>> type(h[3][3][0][1][0])
    <class 'str'>

The parser only generates the levels which are present in the message.

.. doctest::

    >>> type(h[3][1])
    <class 'hl7.containers.Field'>

    >>> type(h[3][1][0])
    <class 'str'>

MLLP network client - ``mllp_send``
-----------------------------------

python-hl7 features a simple network client, ``mllp_send``, which reads HL7
messages from a file or ``sys.stdin`` and posts them to an MLLP server.
``mllp_send`` is a command-line wrapper around
:py:class:`hl7.client.MLLPClient`.  ``mllp_send`` is a useful tool for
testing HL7 interfaces or resending logged messages::

    mllp_send --file sample.hl7 --port 6661 mirth.example.com

See :doc:`mllp_send` for examples and usage instructions.

For receiving HL7 messages using the Minimal Lower Level Protocol (MLLP), take a
look at the related `twisted-hl7 <http://twisted-hl7.readthedocs.org>`_ package.
If do not want to use twisted and are looking to re-write some of twisted-hl7's
functionality, please reach out to us.  It is likely that some of the MLLP
parsing and formatting can be moved into python-hl7, which twisted-hl7 and other
libraries can depend upon.

.. _unicode-vs-byte-strings:

Python 2 vs Python 3 and Unicode vs Byte strings
-------------------------------------------------

python-hl7 supports Python 3.7+ and primarily deals with the unicode ``str`` type.

Passing bytes to :py:func:`hl7.parse`, requires setting the
``encoding`` parameter, if using anything other than UTF-8. :py:func:`hl7.parse`
will always return a datastructure containing unicode ``str`` objects.

:py:class:`hl7.Message` can be forced back into a single string using
and ``str(message)``.

:doc:`mllp_send` assumes the stream is already in the correct encoding.

:py:class:`hl7.client.MLLPClient`, if given a ``str`` or
:py:class:`hl7.Message` instance, will use its ``encoding`` method
to encode the unicode data into bytes.

Contents
--------

.. toctree::
   :maxdepth: 1

   api
   mllp_send
   mllp
   accessors
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
* `HL7v2 Parsing <http://wiki.medical-objects.com.au/index.php/Hl7v2_parsing>`_
* `HL7 Book <http://hl7book.net/index.php?title=HL7_version_2>`_
