# -*- coding: utf-8 -*-
from string import whitespace

from .containers import Factory
from .exceptions import ParseException
from .util import isbatch, isfile, ishl7

_HL7_WHITESPACE = whitespace.replace("\r", "")


def parse_hl7(line, encoding="utf-8", factory=Factory):
    """Returns a instance of the :py:class:`hl7.Message`, :py:class:`hl7.Batch`
    or :py:class:`hl7.File` that allows indexed access to the data elements or
    messages or batches respectively.

    A custom :py:class:`hl7.Factory` subclass can be passed in to be used when
    constructing the message/batch/file and it's components.

    .. note::

        HL7 usually contains only ASCII, but can use other character
        sets (HL7 Standards Document, Section 1.7.1), however as of v2.8,
        UTF-8 is the preferred character set [#]_.

        python-hl7 works on Python unicode strings. :py:func:`hl7.parse_hl7`
        will accept unicode string or will attempt to convert bytestrings
        into unicode strings using the optional ``encoding`` parameter.
        ``encoding`` defaults to UTF-8, so no work is needed for bytestrings
        in UTF-8, but for other character sets like 'cp1252' or 'latin1',
        ``encoding`` must be set appropriately.

    >>> h = hl7.parse_hl7(message)

    To decode a non-UTF-8 byte string::

       hl7.parse_hl7(message, encoding='latin1')

    :rtype: :py:class:`hl7.Message` | :py:class:`hl7.Batch` | :py:class:`hl7.File`

    .. [#] http://wiki.hl7.org/index.php?title=Character_Set_used_in_v2_messages

    """
    # Ensure we are working with unicode data, decode the bytestring
    # if needed
    if isinstance(line, bytes):
        line = line.decode(encoding)
    # If it is an HL7 message, parse as normal
    if ishl7(line):
        return parse(line, encoding=encoding, factory=factory)
    # If we have a batch, then parse the batch
    elif isbatch(line):
        return parse_batch(line, encoding=encoding, factory=factory)
    # If we have a file, parse the HL7 file
    elif isfile(line):
        return parse_file(line, encoding=encoding, factory=factory)
    # Not an HL7 message
    raise ValueError("line is not HL7")


def parse(lines, encoding="utf-8", factory=Factory):
    """Returns a instance of the :py:class:`hl7.Message` that allows
    indexed access to the data elements.

    A custom :py:class:`hl7.Factory` subclass can be passed in to be used when
    constructing the message and it's components.

    .. note::

        HL7 usually contains only ASCII, but can use other character
        sets (HL7 Standards Document, Section 1.7.1), however as of v2.8,
        UTF-8 is the preferred character set [#]_.

        python-hl7 works on Python unicode strings. :py:func:`hl7.parse`
        will accept unicode string or will attempt to convert bytestrings
        into unicode strings using the optional ``encoding`` parameter.
        ``encoding`` defaults to UTF-8, so no work is needed for bytestrings
        in UTF-8, but for other character sets like 'cp1252' or 'latin1',
        ``encoding`` must be set appropriately.

    >>> h = hl7.parse(message)

    To decode a non-UTF-8 byte string::

       hl7.parse(message, encoding='latin1')

    :rtype: :py:class:`hl7.Message`

    .. [#] http://wiki.hl7.org/index.php?title=Character_Set_used_in_v2_messages

    """
    # Ensure we are working with unicode data, decode the bytestring
    # if needed
    if isinstance(lines, bytes):
        lines = lines.decode(encoding)
    # Strip out unnecessary whitespace
    strmsg = lines.strip()
    # The method for parsing the message
    plan = create_parse_plan(strmsg, factory)
    # Start splitting the methods based upon the ParsePlan
    return _split(strmsg, plan)


def _create_batch(batch, messages, encoding, factory):
    """Creates a :py:class:`hl7.Batch`"""
    kwargs = {
        "sequence": [
            parse(message, encoding=encoding, factory=factory) for message in messages
        ],
    }
    # If the BHS/BTS were present, use those to set up the batch
    # otherwise default
    if batch:
        batch = parse(batch, encoding=encoding, factory=factory)
        kwargs["esc"] = batch.esc
        kwargs["separators"] = batch.separators
        kwargs["factory"] = batch.factory
    parsed = factory.create_batch(**kwargs)
    # If the BHS/BTS were present then set them
    if batch:
        parsed.header = batch.segment("BHS")
        try:
            parsed.trailer = batch.segment("BTS")
        except KeyError:
            parsed.trailer = parsed.create_segment([parsed.create_field(["BTS"])])
    return parsed


def parse_batch(lines, encoding="utf-8", factory=Factory):
    """Returns a instance of a :py:class:`hl7.Batch`
    that allows indexed access to the messages.

    A custom :py:class:`hl7.Factory` subclass can be passed in to be used when
    constructing the batch and it's components.

    .. note::

        HL7 usually contains only ASCII, but can use other character
        sets (HL7 Standards Document, Section 1.7.1), however as of v2.8,
        UTF-8 is the preferred character set [#]_.

        python-hl7 works on Python unicode strings. :py:func:`hl7.parse_batch`
        will accept unicode string or will attempt to convert bytestrings
        into unicode strings using the optional ``encoding`` parameter.
        ``encoding`` defaults to UTF-8, so no work is needed for bytestrings
        in UTF-8, but for other character sets like 'cp1252' or 'latin1',
        ``encoding`` must be set appropriately.

    >>> h = hl7.parse_batch(message)

    To decode a non-UTF-8 byte string::

       hl7.parse_batch(message, encoding='latin1')

    :rtype: :py:class:`hl7.Batch`

    .. [#] http://wiki.hl7.org/index.php?title=Character_Set_used_in_v2_messages

    """
    # Ensure we are working with unicode data, decode the bytestring
    # if needed
    if isinstance(lines, bytes):
        lines = lines.decode(encoding)
    batch = None
    messages = []
    # Split the batch into lines, retaining the ends
    for line in lines.strip(_HL7_WHITESPACE).splitlines(keepends=True):
        # strip out all whitespace MINUS the '\r'
        line = line.strip(_HL7_WHITESPACE)
        if line[:3] == "BHS":
            if batch:
                raise ParseException("Batch cannot have more than one BHS segment")
            batch = line
        elif line[:3] == "BTS":
            if not batch or "\rBTS" in batch:
                continue
            batch += line
        elif line[:3] == "MSH":
            messages.append(line)
        else:
            if not messages:
                raise ParseException(
                    "Segment received before message header {}".format(line)
                )
            messages[-1] += line
    return _create_batch(batch, messages, encoding, factory)


def _create_file(file, batches, encoding, factory):
    kwargs = {
        "sequence": [
            _create_batch(batch[0], batch[1], encoding, factory) for batch in batches
        ],
    }
    # If the FHS/FTS are present, use them to set up the file
    if file:
        file = parse(file, encoding=encoding, factory=factory)
        kwargs["esc"] = file.esc
        kwargs["separators"] = file.separators
        kwargs["factory"] = file.factory
    parsed = factory.create_file(**kwargs)
    # If the FHS/FTS are present, add them
    if file:
        parsed.header = file.segment("FHS")
        try:
            parsed.trailer = file.segment("FTS")
        except KeyError:
            parsed.trailer = parsed.create_segment([parsed.create_field(["FTS"])])
    return parsed


def parse_file(lines, encoding="utf-8", factory=Factory):  # noqa: C901
    """Returns a instance of the :py:class:`hl7.File` that allows
    indexed access to the batches.

    A custom :py:class:`hl7.Factory` subclass can be passed in to be used when
    constructing the file and it's components.

    .. note::

        HL7 usually contains only ASCII, but can use other character
        sets (HL7 Standards Document, Section 1.7.1), however as of v2.8,
        UTF-8 is the preferred character set [#]_.

        python-hl7 works on Python unicode strings. :py:func:`hl7.parse_file`
        will accept unicode string or will attempt to convert bytestrings
        into unicode strings using the optional ``encoding`` parameter.
        ``encoding`` defaults to UTF-8, so no work is needed for bytestrings
        in UTF-8, but for other character sets like 'cp1252' or 'latin1',
        ``encoding`` must be set appropriately.

    >>> h = hl7.parse_file(message)

    To decode a non-UTF-8 byte string::

       hl7.parse_file(message, encoding='latin1')

    :rtype: :py:class:`hl7.File`

    .. [#] http://wiki.hl7.org/index.php?title=Character_Set_used_in_v2_messages

    """
    # Ensure we are working with unicode data, decode the bytestring
    # if needed
    if isinstance(lines, bytes):
        lines = lines.decode(encoding)
    file = None
    batches = []
    messages = []
    in_batch = False
    # Split the file into lines, retaining the ends
    for line in lines.strip(_HL7_WHITESPACE).splitlines(keepends=True):
        # strip out all whitespace MINUS the '\r'
        line = line.strip(_HL7_WHITESPACE)
        if line[:3] == "FHS":
            if file:
                raise ParseException("File cannot have more than one FHS segment")
            file = line
        elif line[:3] == "FTS":
            if not file or "\rFTS" in file:
                continue
            file += line
        elif line[:3] == "BHS":
            if in_batch:
                raise ParseException("Batch cannot have more than one BHS segment")
            batches.append([line, []])
            in_batch = True
        elif line[:3] == "BTS":
            if not in_batch:
                continue
            batches[-1][0] += line
            in_batch = False
        elif line[:3] == "MSH":
            if in_batch:
                batches[-1][1].append(line)
            else:  # Messages outside of a batch go into the "default" batch
                messages.append(line)
        else:
            if in_batch:
                if not batches[-1][1]:
                    raise ParseException(
                        "Segment received before message header {}".format(line)
                    )
                batches[-1][1][-1] += line
            else:
                if not messages:
                    raise ParseException(
                        "Segment received before message header {}".format(line)
                    )
                messages[-1] += line
    if messages:  # add the default batch, if we have one
        batches.append([None, messages])
    return _create_file(file, batches, encoding, factory)


def _split(text, plan):
    """Recursive function to split the *text* into an n-deep list,
    according to the :py:class:`hl7._ParsePlan`.
    """
    # Base condition, if we have used up all the plans
    if not plan:
        return text

    if not plan.applies(text):
        return plan.container([text])

    # Parsing of the first segment is awkward because it contains
    # the separator characters in a field
    if plan.containers[0] == plan.factory.create_segment and text[:3] in [
        "MSH",
        "BHS",
        "FHS",
    ]:
        seg = text[:3]
        sep0 = text[3]
        sep_end_off = text.find(sep0, 4)
        seps = text[4:sep_end_off]
        text = text[sep_end_off + 1 :]
        data = [
            plan.factory.create_field(
                sequence=[seg], esc=plan.esc, separators=plan.separators
            ),
            plan.factory.create_field(
                sequence=[sep0], esc=plan.esc, separators=plan.separators
            ),
            plan.factory.create_field(
                sequence=[seps], esc=plan.esc, separators=plan.separators
            ),
        ]
    else:
        data = []

    if text:
        data = data + [_split(x, plan.next()) for x in text.split(plan.separator)]
    # Return the instance of the current message part according
    # to the plan
    return plan.container(data)


def create_parse_plan(strmsg, factory=Factory):
    """Creates a plan on how to parse the HL7 message according to
    the details stored within the message.
    """
    # We will always use a carriage return to separate segments
    separators = "\r"

    # Extract the rest of the separators. Defaults used if not present.
    if strmsg[:3] not in ("MSH", "FHS", "BHS"):
        raise ParseException(
            "First segment is {}, must be one of MHS, FHS or BHS".format(strmsg[:3])
        )
    sep0 = strmsg[3]
    seps = list(strmsg[3 : strmsg.find(sep0, 4)])

    separators += seps[0]
    if len(seps) > 2:
        separators += seps[2]  # repetition separator
    else:
        separators += "~"  # repetition separator
    if len(seps) > 1:
        separators += seps[1]  # component separator
    else:
        separators += "^"  # component separator
    if len(seps) > 4:
        separators += seps[4]  # sub-component separator
    else:
        separators += "&"  # sub-component separator
    if len(seps) > 3:
        esc = seps[3]
    else:
        esc = "\\"

    # The ordered list of containers to create
    containers = [
        factory.create_message,
        factory.create_segment,
        factory.create_field,
        factory.create_repetition,
        factory.create_component,
    ]
    return _ParsePlan(separators[0], separators, containers, esc, factory)


class _ParsePlan(object):
    """Details on how to parse an HL7 message. Typically this object
    should be created via :func:`hl7.create_parse_plan`
    """

    # field, component, repetition, escape, subcomponent

    def __init__(self, seperator, separators, containers, esc, factory):
        # TODO test to see performance implications of the assertion
        # since we generate the ParsePlan, this should never be in
        # invalid state
        assert len(containers) == len(separators[separators.find(seperator) :])
        self.separator = seperator
        self.separators = separators
        self.containers = containers
        self.esc = esc
        self.factory = factory

    def container(self, data):
        """Return an instance of the appropriate container for the *data*
        as specified by the current plan.
        """
        return self.containers[0](
            sequence=data,
            esc=self.esc,
            separators=self.separators,
            factory=self.factory,
        )

    def next(self):
        """Generate the next level of the plan (essentially generates
        a copy of this plan with the level of the container and the
        seperator starting at the next index.
        """
        if len(self.containers) > 1:
            # Return a new instance of this class using the tails of
            # the separators and containers lists. Use self.__class__()
            # in case :class:`hl7.ParsePlan` is subclassed
            return self.__class__(
                self.separators[self.separators.find(self.separator) + 1],
                self.separators,
                self.containers[1:],
                self.esc,
                self.factory,
            )
        # When we have no separators and containers left, return None,
        # which indicates that we have nothing further.
        return None

    def applies(self, text):
        """return True if the separator or those if the children are in the text"""
        for s in self.separators[self.separators.find(self.separator) :]:
            if text.find(s) >= 0:
                return True
        return False
