# -*- coding: utf-8 -*-
import datetime
import logging

from .accessor import Accessor
from .exceptions import (
    MalformedBatchException,
    MalformedFileException,
    MalformedSegmentException,
)
from .util import escape, generate_message_control_id, unescape

logger = logging.getLogger(__file__)

_SENTINEL = object()


class Sequence(list):
    """Base class for sequences that can be indexed using 1-based index"""

    def __call__(self, index, value=_SENTINEL):
        """Support list access using HL7 compatible 1-based indices.
        Can be used to get and set values.

        >>> s = hl7.Sequence([1, 2, 3, 4])
        >>> s(1) == s[0]
        True
        >>> s(2, "new")
        >>> s
        [1, 'new', 3, 4]
        """
        index = self._adjust_index(int(index))
        if value is _SENTINEL:
            return self[index]
        else:
            self[index] = value

    def _adjust_index(self, index):
        """Subclasses can override if they do not want HL7 1-based indexing when used as callable"""
        if index >= 1:
            return index - 1
        else:
            return index


class Container(Sequence):
    """Abstract root class for the parts of the HL7 message."""

    def __init__(
        self, separator, sequence=[], esc="\\", separators="\r|~^&", factory=None
    ):
        assert separator in separators
        # Initialize the list object, optionally passing in the
        # sequence.  Since list([]) == [], using the default
        # parameter will not cause any issues.
        super(Container, self).__init__(sequence)
        self.separator = separator
        self.esc = esc
        self.separators = separators
        self.factory = factory if factory is not None else Factory

    def create_file(self, seq):
        """Create a new :py:class:`hl7.File` compatible with this container"""
        return self.factory.create_file(
            sequence=seq,
            esc=self.esc,
            separators=self.separators,
            factory=self.factory,
        )

    def create_batch(self, seq):
        """Create a new :py:class:`hl7.Batch` compatible with this container"""
        return self.factory.create_batch(
            sequence=seq,
            esc=self.esc,
            separators=self.separators,
            factory=self.factory,
        )

    def create_message(self, seq):
        """Create a new :py:class:`hl7.Message` compatible with this container"""
        return self.factory.create_message(
            sequence=seq,
            esc=self.esc,
            separators=self.separators,
            factory=self.factory,
        )

    def create_segment(self, seq):
        """Create a new :py:class:`hl7.Segment` compatible with this container"""
        return self.factory.create_segment(
            sequence=seq,
            esc=self.esc,
            separators=self.separators,
            factory=self.factory,
        )

    def create_field(self, seq):
        """Create a new :py:class:`hl7.Field` compatible with this container"""
        return self.factory.create_field(
            sequence=seq,
            esc=self.esc,
            separators=self.separators,
            factory=self.factory,
        )

    def create_repetition(self, seq):
        """Create a new :py:class:`hl7.Repetition` compatible with this container"""
        return self.factory.create_repetition(
            sequence=seq,
            esc=self.esc,
            separators=self.separators,
            factory=self.factory,
        )

    def create_component(self, seq):
        """Create a new :py:class:`hl7.Component` compatible with this container"""
        return self.factory.create_component(
            sequence=seq,
            esc=self.esc,
            separators=self.separators,
            factory=self.factory,
        )

    def __getitem__(self, item):
        # Python slice operator was returning a regular list, not a
        # Container subclass
        sequence = super(Container, self).__getitem__(item)
        if isinstance(item, slice):
            return self.__class__(
                self.separator,
                sequence,
                self.esc,
                self.separators,
                factory=self.factory,
            )
        return sequence

    def __getslice__(self, i, j):
        # Python 2.x compatibility.  __getslice__ is deprecated, and
        # we want to wrap the logic from __getitem__ when handling slices
        return self.__getitem__(slice(i, j))

    def __str__(self):
        return self.separator.join((str(x) for x in self))


class File(Container):
    """Representation of an HL7 file from the batch protocol.
    It contains a list of :py:class:`hl7.Batch`
    instances. It may contain FHS/FTS :py:class:`hl7.Segment` instances.

    Files may or may not be wrapped in FHS/FTS segements
    deliniating the start/end of the batch. These are optional.
    """

    def __init__(
        self, separator=None, sequence=[], esc="\\", separators="\r|~^&", factory=None
    ):
        assert not separator or separator == separators[0]
        super(File, self).__init__(
            separator=separators[0],
            sequence=sequence,
            esc=esc,
            separators=separators,
            factory=factory,
        )
        self.header = None
        self.trailer = None

    @property
    def header(self):
        """FHS :py:class:`hl7.Segment`"""
        return self._batch_header_segment

    @header.setter
    def header(self, segment):
        if segment and segment[0][0] != "FHS":
            raise MalformedSegmentException('header must begin with "FHS"')
        self._batch_header_segment = segment

    @property
    def trailer(self):
        """FTS :py:class:`hl7.Segment`"""
        return self._batch_trailer_segment

    @trailer.setter
    def trailer(self, segment):
        if segment and segment[0][0] != "FTS":
            raise MalformedSegmentException('trailer must begin with "FTS"')
        self._batch_trailer_segment = segment

    def create_header(self):
        """Create a new :py:class:`hl7.Segment` FHS compatible with this file"""
        return self.create_segment(
            [
                self.create_field(["FHS"]),
                self.create_field([self.separators[1]]),
                self.create_field(
                    [
                        self.separators[3]
                        + self.separators[2]
                        + self.esc
                        + self.separators[4]
                    ]
                ),
            ]
        )

    def create_trailer(self):
        """Create a new :py:class:`hl7.Segment` FTS compatible with this file"""
        return self.create_segment([self.create_field(["FTS"])])

    def __str__(self):
        """Join a the child batches into a single string, separated
        by the self.separator.  This method acts recursively, calling
        the children's __unicode__ method.  Thus ``unicode()`` is the
        approriate method for turning the python-hl7 representation of
        HL7 into a standard string.

        If this batch has FHS/FTS segments, they will be added to the
        beginning/end of the returned string.
        """
        if (self.header and not self.trailer) or (not self.header and self.trailer):
            raise MalformedFileException(
                "Either both header and trailer must be present or neither"
            )
        return (
            super(File, self).__str__()
            if not self.header
            else str(self.header)
            + self.separator
            + super(File, self).__str__()
            + str(self.trailer)
            + self.separator
        )


class Batch(Container):
    """Representation of an HL7 batch from the batch protocol.
    It contains a list of :py:class:`hl7.Message` instances.
    It may contain BHS/BTS :py:class:`hl7.Segment` instances.

    Batches may or may not be wrapped in BHS/BTS segements
    deliniating the start/end of the batch. These are optional.
    """

    def __init__(
        self, separator=None, sequence=[], esc="\\", separators="\r|~^&", factory=None
    ):
        assert not separator or separator == separators[0]
        super(Batch, self).__init__(
            separator=separators[0],
            sequence=sequence,
            esc=esc,
            separators=separators,
            factory=factory,
        )
        self.header = None
        self.trailer = None

    @property
    def header(self):
        """BHS :py:class:`hl7.Segment`"""
        return self._batch_header_segment

    @header.setter
    def header(self, segment):
        if segment and segment[0][0] != "BHS":
            raise MalformedSegmentException('header must begin with "BHS"')
        self._batch_header_segment = segment

    @property
    def trailer(self):
        """BTS :py:class:`hl7.Segment`"""
        return self._batch_trailer_segment

    @trailer.setter
    def trailer(self, segment):
        if segment and segment[0][0] != "BTS":
            raise MalformedSegmentException('trailer must begin with "BTS"')
        self._batch_trailer_segment = segment

    def create_header(self):
        """Create a new :py:class:`hl7.Segment` BHS compatible with this batch"""
        return self.create_segment(
            [
                self.create_field(["BHS"]),
                self.create_field([self.separators[1]]),
                self.create_field(
                    [
                        self.separators[3]
                        + self.separators[2]
                        + self.esc
                        + self.separators[4]
                    ]
                ),
            ]
        )

    def create_trailer(self):
        """Create a new :py:class:`hl7.Segment` BHS compatible with this batch"""
        return self.create_segment([self.create_field(["BTS"])])

    def __str__(self):
        """Join a the child messages into a single string, separated
        by the self.separator.  This method acts recursively, calling
        the children's __unicode__ method.  Thus ``unicode()`` is the
        approriate method for turning the python-hl7 representation of
        HL7 into a standard string.

        If this batch has BHS/BTS segments, they will be added to the
        beginning/end of the returned string.
        """
        if (self.header and not self.trailer) or (not self.header and self.trailer):
            raise MalformedBatchException(
                "Either both header and trailer must be present or neither"
            )
        return (
            super(Batch, self).__str__()
            if not self.header
            else str(self.header)
            + self.separator
            + super(Batch, self).__str__()
            + str(self.trailer)
            + self.separator
        )


class Message(Container):
    def __init__(
        self, separator=None, sequence=[], esc="\\", separators="\r|~^&", factory=None
    ):
        assert not separator or separator == separators[0]
        super(Message, self).__init__(
            separator=separators[0],
            sequence=sequence,
            esc=esc,
            separators=separators,
            factory=factory,
        )

    """Representation of an HL7 message. It contains a list
    of :py:class:`hl7.Segment` instances.
    """

    def __getitem__(self, key):
        """Index, segment-based or accessor lookup.

        If key is an integer, ``__getitem__`` acts list a list, returning
        the :py:class:`hl7.Segment` held at that index:

        >>> h[1]  # doctest: +ELLIPSIS
        [['PID'], ...]

        If the key is a string of length 3, ``__getitem__`` acts like a dictionary,
        returning all segments whose *segment_id* is *key*
        (alias of :py:meth:`hl7.Message.segments`).

        >>> h['OBX']  # doctest: +ELLIPSIS
        [[['OBX'], ['1'], ...]]

        If the key is a string of length greater than 3,
        the key is parsed into an :py:class:`hl7.Accessor` and passed
        to :py:meth:`hl7.Message.extract_field`.

        If the key is an :py:class:`hl7.Accessor`, it is passed to
        :py:meth:`hl7.Message.extract_field`.
        """
        if isinstance(key, str):
            if len(key) == 3:
                return self.segments(key)
            return self.extract_field(*Accessor.parse_key(key))
        elif isinstance(key, Accessor):
            return self.extract_field(*key)
        return super(Message, self).__getitem__(key)

    def __setitem__(self, key, value):
        """Index or accessor assignment.

        If key is an integer, ``__setitem__`` acts list a list, setting
        the :py:class:`hl7.Segment` held at that index:

        >>> h[1] = hl7.Segment("|", [hl7.Field("~", ['PID'], [''])])

        If the key is a string of length greater than 3,
        the key is parsed into an :py:class:`hl7.Accessor` and passed
        to :py:meth:`hl7.Message.assign_field`.

        >>> h["PID.2"] = "NEW"

        If the key is an :py:class:`hl7.Accessor`, it is passed to
        :py:meth:`hl7.Message.assign_field`.
        """
        if isinstance(key, str) and len(key) > 3 and isinstance(value, str):
            return self.assign_field(value, *Accessor.parse_key(key))
        elif isinstance(key, Accessor):
            return self.assign_field(value, *key)
        return super(Message, self).__setitem__(key, value)

    def segment(self, segment_id):
        """Gets the first segment with the *segment_id* from the parsed
        *message*.

        >>> h.segment('PID')  # doctest: +ELLIPSIS
        [['PID'], ...]

        :rtype: :py:class:`hl7.Segment`
        """
        # Get the list of all the segments and pull out the first one,
        # if possible
        match = self.segments(segment_id)
        # We should never get an IndexError, since segments will instead
        # throw an KeyError
        return match[0]

    def segments(self, segment_id):
        """Returns the requested segments from the parsed *message* that are
        identified by the *segment_id* (e.g. OBR, MSH, ORC, OBX).

        >>> h.segments('OBX')
        [[['OBX'], ['1'], ...]]

        :rtype: list of :py:class:`hl7.Segment`
        """
        # Compare segment_id to the very first string in each segment,
        # returning all segments that match.
        # Return as a Sequence so 1-based indexing can be used
        matches = Sequence(segment for segment in self if segment[0][0] == segment_id)
        if len(matches) == 0:
            raise KeyError("No %s segments" % segment_id)
        return matches

    def extract_field(
        self,
        segment,
        segment_num=1,
        field_num=1,
        repeat_num=1,
        component_num=1,
        subcomponent_num=1,
    ):
        """
        Extract a field using a future proofed approach, based on rules in:
        http://wiki.medical-objects.com.au/index.php/Hl7v2_parsing

        'PID|Field1|Component1^Component2|Component1^Sub-Component1&Sub-Component2^Component3|Repeat1~Repeat2',

            |   PID.F3.R1.C2.S2 = 'Sub-Component2'
            |   PID.F4.R2.C1 = 'Repeat1'

        Compatibility Rules:

            If the parse tree is deeper than the specified path continue
            following the first child branch until a leaf of the tree is
            encountered and return that value (which could be blank).

            Example:

                |   PID.F3.R1.C2 = 'Sub-Component1' (assume .SC1)

            If the parse tree terminates before the full path is satisfied
            check each of the subsequent paths and if every one is specified
            at position 1 then the leaf value reached can be returned as the
            result.

                |   PID.F4.R1.C1.SC1 = 'Repeat1'    (ignore .SC1)
        """
        return self.segments(segment)(segment_num).extract_field(
            segment_num, field_num, repeat_num, component_num, subcomponent_num
        )

    def assign_field(
        self,
        value,
        segment,
        segment_num=1,
        field_num=None,
        repeat_num=None,
        component_num=None,
        subcomponent_num=None,
    ):
        """
        Assign a value into a message using the tree based assignment notation.
        The segment must exist.

        Extract a field using a future proofed approach, based on rules in:
        http://wiki.medical-objects.com.au/index.php/Hl7v2_parsing
        """
        self.segments(segment)(segment_num).assign_field(
            value, field_num, repeat_num, component_num, subcomponent_num
        )

    def escape(self, field, app_map=None):
        """
        See: http://www.hl7standards.com/blog/2006/11/02/hl7-escape-sequences/

        To process this correctly, the full set of separators (MSH.1/MSH.2) needs to be known.

        Pass through the message. Replace recognised characters with their escaped
        version. Return an ascii encoded string.

        Functionality:

        *   Replace separator characters (2.10.4)
        *   replace application defined characters (2.10.7)
        *   Replace non-ascii values with hex versions using HL7 conventions.

        Incomplete:

        *   replace highlight characters (2.10.3)
        *   How to handle the rich text substitutions.
        *   Merge contiguous hex values
        """
        return escape(self, field, app_map)

    def unescape(self, field, app_map=None):
        """
        See: http://www.hl7standards.com/blog/2006/11/02/hl7-escape-sequences/

        To process this correctly, the full set of separators (MSH.1/MSH.2) needs to be known.

        This will convert the identifiable sequences.
        If the application provides mapping, these are also used.
        Items which cannot be mapped are removed

        For example, the App Map count provide N, H, Zxxx values

        Chapter 2: Section 2.10

        At the moment, this functionality can:

        *   replace the parsing characters (2.10.4)
        *   replace highlight characters (2.10.3)
        *   replace hex characters. (2.10.5)
        *   replace rich text characters (2.10.6)
        *   replace application defined characters (2.10.7)

        It cannot:

        *   switch code pages / ISO IR character sets
        """
        return unescape(self, field, app_map)

    def create_ack(
        self, ack_code="AA", message_id=None, application=None, facility=None
    ):
        """
        Create an hl7 ACK response :py:class:`hl7.Message`, per spec 2.9.2, for this message.

        See http://www.hl7standards.com/blog/2007/02/01/ack-message-original-mode-acknowledgement/

        ``ack_code`` options are one of `AA` (Application Accept), `AR` (Application Reject),
        `AE` (Application Error), `CA` (Commit Accept - Enhanced Mode),
        `CR` (Commit Reject - Enhanced Mode), or `CE` (Commit Error - Enhanced Mode)
        (see HL7 Table 0008 - Acknowledgment Code)
        ``message_id`` control message ID for ACK, defaults to unique generated ID
        ``application`` name of sending application, defaults to receiving application of message
        ``facility`` name of sending facility, defaults to receiving facility of message
        """
        source_msh = self.segment("MSH")
        msh = self.create_segment([self.create_field(["MSH"])])

        msh.assign_field(str(source_msh(1)), 1)
        msh.assign_field(str(source_msh(2)), 2)
        # Sending application is source receving application
        msh.assign_field(
            str(application) if application is not None else str(source_msh(5)), 3
        )
        # Sending facility is source receving facility
        msh.assign_field(
            str(facility) if facility is not None else str(source_msh(6)), 4
        )
        # Receiving application is source sending application
        msh.assign_field(str(source_msh(3)), 5)
        # Receiving facility is source sending facility
        msh.assign_field(str(source_msh(4)), 6)
        msh.assign_field(str(datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")), 7)
        # Message type code
        msh.assign_field("ACK", 9, 1, 1)
        # Copy trigger event from source
        msh.assign_field(str(source_msh(9)(1)(2)), 9, 1, 2)
        msh.assign_field("ACK", 9, 1, 3)
        msh.assign_field(
            message_id if message_id is not None else generate_message_control_id(), 10
        )
        msh.assign_field(str(source_msh(11)), 11)
        msh.assign_field(str(source_msh(12)), 12)

        msa = self.create_segment([self.create_field(["MSA"])])
        msa.assign_field(str(ack_code), 1)
        msa.assign_field(str(source_msh(10)), 2)
        ack = self.create_message([msh, msa])

        return ack

    def __str__(self):
        """Join a the child containers into a single string, separated
        by the self.separator.  This method acts recursively, calling
        the children's __unicode__ method.  Thus ``unicode()`` is the
        approriate method for turning the python-hl7 representation of
        HL7 into a standard string.

        >>> str(hl7.parse(message)) == message
        True

        """
        # Per spec, Message Construction Rules, Section 2.6 (v2.8), Message ends
        # with the carriage return
        return super(Message, self).__str__() + self.separator


class Segment(Container):
    def __init__(
        self, separator=None, sequence=[], esc="\\", separators="\r|~^&", factory=None
    ):
        assert not separator or separator == separators[1]
        super(Segment, self).__init__(
            separator=separators[1],
            sequence=sequence,
            esc=esc,
            separators=separators,
            factory=factory,
        )

    """Second level of an HL7 message, which represents an HL7 Segment.
    Traditionally this is a line of a message that ends with a carriage
    return and is separated by pipes. It contains a list of
    :py:class:`hl7.Field` instances.
    """

    def extract_field(
        self,
        segment_num=1,
        field_num=1,
        repeat_num=1,
        component_num=1,
        subcomponent_num=1,
    ):
        """
        Extract a field using a future proofed approach, based on rules in:
        http://wiki.medical-objects.com.au/index.php/Hl7v2_parsing

        'PID|Field1|Component1^Component2|Component1^Sub-Component1&Sub-Component2^Component3|Repeat1~Repeat2',

            |   F3.R1.C2.S2 = 'Sub-Component2'
            |   F4.R2.C1 = 'Repeat1'

        Compatibility Rules:

            If the parse tree is deeper than the specified path continue
            following the first child branch until a leaf of the tree is
            encountered and return that value (which could be blank).

            Example:

                |   F3.R1.C2 = 'Sub-Component1' (assume .SC1)

            If the parse tree terminates before the full path is satisfied
            check each of the subsequent paths and if every one is specified
            at position 1 then the leaf value reached can be returned as the
            result.

                |   F4.R1.C1.SC1 = 'Repeat1'    (ignore .SC1)
        """
        # Save original values for error messages
        accessor = Accessor(
            self[0][0],
            segment_num,
            field_num,
            repeat_num,
            component_num,
            subcomponent_num,
        )

        field_num = field_num or 1
        repeat_num = repeat_num or 1
        component_num = component_num or 1
        subcomponent_num = subcomponent_num or 1

        if field_num < len(self):
            field = self(field_num)
        else:
            if repeat_num == 1 and component_num == 1 and subcomponent_num == 1:
                return ""  # Assume non-present optional value
            raise IndexError("Field not present: {0}".format(accessor.key))

        rep = field(repeat_num)

        if not isinstance(rep, Repetition):
            # leaf
            if component_num == 1 and subcomponent_num == 1:
                return (
                    rep
                    if accessor.segment == "MSH" and accessor.field_num in (1, 2)
                    else unescape(self, rep)
                )
            raise IndexError(
                "Field reaches leaf node before completing path: {0}".format(
                    accessor.key
                )
            )

        if component_num > len(rep):
            if subcomponent_num == 1:
                return ""  # Assume non-present optional value
            raise IndexError("Component not present: {0}".format(accessor.key))

        component = rep(component_num)
        if not isinstance(component, Component):
            # leaf
            if subcomponent_num == 1:
                return unescape(self, component)
            raise IndexError(
                "Field reaches leaf node before completing path: {0}".format(
                    accessor.key
                )
            )

        if subcomponent_num <= len(component):
            subcomponent = component(subcomponent_num)
            return unescape(self, subcomponent)
        else:
            return ""  # Assume non-present optional value

    def assign_field(
        self,
        value,
        field_num=None,
        repeat_num=None,
        component_num=None,
        subcomponent_num=None,
    ):
        """
        Assign a value into a message using the tree based assignment notation.
        The segment must exist.

        Extract a field using a future proofed approach, based on rules in:
        http://wiki.medical-objects.com.au/index.php/Hl7v2_parsing
        """

        while len(self) <= field_num:
            self.append(self.create_field([]))
        field = self(field_num)
        if repeat_num is None:
            field[:] = [value]
            return
        while len(field) < repeat_num:
            field.append(self.create_repetition([]))
        repetition = field(repeat_num)
        if component_num is None:
            repetition[:] = [value]
            return
        while len(repetition) < component_num:
            repetition.append(self.create_component([]))
        component = repetition(component_num)
        if subcomponent_num is None:
            component[:] = [value]
            return
        while len(component) < subcomponent_num:
            component.append("")
        component(subcomponent_num, value)

    def _adjust_index(self, index):
        # First element is the segment name, so we don't need to adjust to get 1-based
        return index

    def __str__(self):
        if str(self[0]) in ["MSH", "FHS", "BHS"]:
            return (
                str(self[0])
                + str(self[1])
                + str(self[2])
                + str(self[1])
                + self.separator.join((str(x) for x in self[3:]))
            )
        return super(Segment, self).__str__()


class Field(Container):
    def __init__(
        self, separator=None, sequence=[], esc="\\", separators="\r|~^&", factory=None
    ):
        assert not separator or separator == separators[2]
        super(Field, self).__init__(
            separator=separators[2],
            sequence=sequence,
            esc=esc,
            separators=separators,
            factory=factory,
        )

    """Third level of an HL7 message, that traditionally is surrounded
    by pipes and separated by carets. It contains a list of strings
    or :py:class:`hl7.Repetition` instances.
    """


class Repetition(Container):
    def __init__(
        self, separator=None, sequence=[], esc="\\", separators="\r|~^&", factory=None
    ):
        assert not separator or separator == separators[3]
        super(Repetition, self).__init__(
            separator=separators[3],
            sequence=sequence,
            esc=esc,
            separators=separators,
            factory=factory,
        )

    """Fourth level of an HL7 message. A field can repeat.
    It contains a list of strings or :py:class:`hl7.Component` instances.
    """


class Component(Container):
    def __init__(
        self, separator=None, sequence=[], esc="\\", separators="\r|~^&", factory=None
    ):
        assert not separator or separator == separators[4]
        super(Component, self).__init__(
            separator=separators[4],
            sequence=sequence,
            esc=esc,
            separators=separators,
            factory=factory,
        )

    """Fifth level of an HL7 message. A component is a composite datatypes.
    It contains a list of string sub-components.
    """


class Factory(object):
    """Factory used to create each type of Container.

    A subclass can be used to create specialized subclasses of each container.
    """

    create_file = File  #: Create an instance of :py:class:`hl7.File`
    create_batch = Batch  #: Create an instance of :py:class:`hl7.Batch`
    create_message = Message  #: Create an instance of :py:class:`hl7.Message`
    create_segment = Segment  #: Create an instance of :py:class:`hl7.Segment`
    create_field = Field  #: Create an instance of :py:class:`hl7.Field`
    create_repetition = Repetition  #: Create an instance of :py:class:`hl7.Repetition`
    create_component = Component  #: Create an instance of :py:class:`hl7.Component`
