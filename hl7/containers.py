# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import logging
import six
from .compat import python_2_unicode_compatible
from .accessor import Accessor
from .util import generate_message_control_id

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


@python_2_unicode_compatible
class Container(Sequence):
    """Abstract root class for the parts of the HL7 message."""
    def __init__(self, separator, sequence=[], esc='\\', separators='\r|~^&', factory=None):
        # Initialize the list object, optionally passing in the
        # sequence.  Since list([]) == [], using the default
        # parameter will not cause any issues.
        super(Container, self).__init__(sequence)
        self.separator = separator
        self.esc = esc
        self.separators = separators
        self.factory = factory if factory is not None else Factory

    def __getitem__(self, item):
        # Python slice operator was returning a regular list, not a
        # Container subclass
        sequence = super(Container, self).__getitem__(item)
        if isinstance(item, slice):
            return self.__class__(
                self.separator, sequence, self.esc, self.separators, factory=self.factory
            )
        return sequence

    def __getslice__(self, i, j):
        # Python 2.x compatibility.  __getslice__ is deprecated, and
        # we want to wrap the logic from __getitem__ when handling slices
        return self.__getitem__(slice(i, j))

    def __str__(self):
        """Join a the child containers into a single string, separated
        by the self.separator.  This method acts recursively, calling
        the children's __unicode__ method.  Thus ``unicode()`` is the
        approriate method for turning the python-hl7 representation of
        HL7 into a standard string.

        >>> unicode(h) == message
        True

        .. note::
           For Python 2.x use ``unicode()``, but for Python 3.x, use
           ``str()``

        """
        return self.separator.join((six.text_type(x) for x in self))


class Message(Container):
    """Representation of an HL7 message. It contains a list
    of :py:class:`hl7.Segment` instances.
    """
    def __getitem__(self, key):
        """Index, segment-based or accessor lookup.

        If key is an integer, ``__getitem__`` acts list a list, returning
        the :py:class:`hl7.Segment` held at that index:

        >>> h[1]  # doctest: +ELLIPSIS
        [[u'PID'], ...]

        If the key is a string of length 3, ``__getitem__`` acts like a dictionary,
        returning all segments whose *segment_id* is *key*
        (alias of :py:meth:`hl7.Message.segments`).

        >>> h['OBX']  # doctest: +ELLIPSIS
        [[[u'OBX'], [u'1'], ...]]

        If the key is a string of length greater than 3,
        the key is parsed into an :py:class:`hl7.Accessor` and passed
        to :py:meth:`hl7.Message.extract_field`.

        If the key is an :py:class:`hl7.Accessor`, it is passed to
        :py:meth:`hl7.Message.extract_field`.
        """
        if isinstance(key, six.string_types):
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

        >>> h[1] = hl7.Segment("|", [hl7.Field("^", [u'PID'], [u''])])

        If the key is a string of length greater than 3,
        the key is parsed into an :py:class:`hl7.Accessor` and passed
        to :py:meth:`hl7.Message.assign_field`.

        >>> h["PID.2"] = "NEW"

        If the key is an :py:class:`hl7.Accessor`, it is passed to
        :py:meth:`hl7.Message.assign_field`.
        """
        if isinstance(key, six.string_types) and len(key) > 3 and isinstance(value, six.string_types):
            return self.assign_field(value, *Accessor.parse_key(key))
        elif isinstance(key, Accessor):
            return self.assign_field(value, *key)
        return super(Message, self).__setitem__(key, value)

    def segment(self, segment_id):
        """Gets the first segment with the *segment_id* from the parsed
        *message*.

        >>> h.segment('PID')  # doctest: +ELLIPSIS
        [[u'PID'], ...]

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
        [[[u'OBX'], [u'1'], ...]]

        :rtype: list of :py:class:`hl7.Segment`
        """
        # Compare segment_id to the very first string in each segment,
        # returning all segments that match.
        # Return as a Sequence so 1-based indexing can be used
        matches = Sequence(segment for segment in self if segment[0][0] == segment_id)
        if len(matches) == 0:
            raise KeyError('No %s segments' % segment_id)
        return matches

    def extract_field(self, segment, segment_num=1, field_num=1, repeat_num=1, component_num=1, subcomponent_num=1):
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
        # Save original values for error messages
        accessor = Accessor(segment, segment_num, field_num, repeat_num, component_num, subcomponent_num)

        field_num = field_num or 1
        repeat_num = repeat_num or 1
        component_num = component_num or 1
        subcomponent_num = subcomponent_num or 1

        segment = self.segments(segment)(segment_num)
        if field_num < len(segment):
            field = segment(field_num)
        else:
            if repeat_num == 1 and component_num == 1 and subcomponent_num == 1:
                return ''  # Assume non-present optional value
            raise IndexError('Field not present: {0}'.format(accessor.key))

        rep = field(repeat_num)

        if not isinstance(rep, Repetition):
            # leaf
            if component_num == 1 and subcomponent_num == 1:
                return self.unescape(rep)
            raise IndexError('Field reaches leaf node before completing path: {0}'.format(accessor.key))

        if component_num > len(rep):
            if subcomponent_num == 1:
                return ''  # Assume non-present optional value
            raise IndexError('Component not present: {0}'.format(accessor.key))

        component = rep(component_num)
        if not isinstance(component, Component):
            # leaf
            if subcomponent_num == 1:
                return self.unescape(component)
            raise IndexError('Field reaches leaf node before completing path: {0}'.format(accessor.key))

        if subcomponent_num <= len(component):
            subcomponent = component(subcomponent_num)
            return self.unescape(subcomponent)
        else:
            return ''  # Assume non-present optional value

    def assign_field(self, value, segment, segment_num=1, field_num=None, repeat_num=None, component_num=None, subcomponent_num=None):
        """
            Assign a value into a message using the tree based assignment notation.
            The segment must exist.

            Extract a field using a future proofed approach, based on rules in:
            http://wiki.medical-objects.com.au/index.php/Hl7v2_parsing
        """
        segment = self.segments(segment)(segment_num)

        while len(segment) <= field_num:
            segment.append(self.create_field([]))
        field = segment(field_num)
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
            component.append('')
        component(subcomponent_num, value)

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
        if not field:
            return field

        esc = str(self.esc)

        DEFAULT_MAP = {
            self.separators[1]: 'F',  # 2.10.4
            self.separators[2]: 'R',
            self.separators[3]: 'S',
            self.separators[4]: 'T',
            self.esc: 'E',
            '\r': '.br',  # 2.10.6
        }

        rv = []
        for offset, c in enumerate(field):
            if app_map and c in app_map:
                rv.append(esc + app_map[c] + esc)
            elif c in DEFAULT_MAP:
                rv.append(esc + DEFAULT_MAP[c] + esc)
            elif ord(c) >= 0x20 and ord(c) <= 0x7E:
                rv.append(c.encode('ascii'))
            else:
                rv.append('%sX%2x%s' % (esc, ord(c), esc))

        return ''.join(rv)

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
        if not field or field.find(self.esc) == -1:
            return field

        DEFAULT_MAP = {
            'H': '_',  # Override using the APP MAP: 2.10.3
            'N': '_',  # Override using the APP MAP
            'F': self.separators[1],  # 2.10.4
            'R': self.separators[2],
            'S': self.separators[3],
            'T': self.separators[4],
            'E': self.esc,
            '.br': '\r',  # 2.10.6
            '.sp': '\r',
            '.fi': '',
            '.nf': '',
            '.in': '    ',
            '.ti': '    ',
            '.sk': ' ',
            '.ce': '\r',
        }

        rv = []
        collecting = []
        in_seq = False
        for offset, c in enumerate(field):
            if in_seq:
                if c == self.esc:
                    in_seq = False
                    value = ''.join(collecting)
                    collecting = []
                    if not value:
                        logger.warn('Error unescaping value [%s], empty sequence found at %d', field, offset)
                        continue
                    if app_map and value in app_map:
                        rv.append(app_map[value])
                    elif value in DEFAULT_MAP:
                        rv.append(DEFAULT_MAP[value])
                    elif value.startswith('.') and ((app_map and value[:3] in app_map) or value[:3] in DEFAULT_MAP):
                        # Substitution with a number of repetitions defined (2.10.6)
                        if app_map and value[:3] in app_map:
                            ch = app_map[value[:3]]
                        else:
                            ch = DEFAULT_MAP[value[:3]]
                        count = int(value[3:])
                        rv.append(ch * count)

                    elif value[0] == 'C':  # Convert to new Single Byte character set : 2.10.2
                        # Two HEX values, first value chooses the character set (ISO-IR), second gives the value
                        logger.warn('Error inline character sets [%s] not implemented, field [%s], offset [%s]', value, field, offset)
                    elif value[0] == 'M':  # Switch to new Multi Byte character set : 2.10.2
                        # Three HEX values, first value chooses the character set (ISO-IR), rest give the value
                        logger.warn('Error inline character sets [%s] not implemented, field [%s], offset [%s]', value, field, offset)
                    elif value[0] == 'X':  # Hex encoded Bytes: 2.10.5
                        value = value[1:]
                        try:
                            for off in range(0, len(value), 2):
                                rv.append(six.unichr(int(value[off:off + 2], 16)))
                        except:
                            logger.exception('Error decoding hex value [%s], field [%s], offset [%s]', value, field, offset)
                    else:
                        logger.exception('Error decoding value [%s], field [%s], offset [%s]', value, field, offset)
                else:
                    collecting.append(c)
            elif c == self.esc:
                in_seq = True
            else:
                rv.append(six.text_type(c))

        return ''.join(rv)

    def create_message(self, seq):
        """Create a new :py:class:`hl7.Message` compatible with this message"""
        return self.factory.create_message(self.separators[0], seq, esc=self.esc, separators=self.separators, factory=self.factory)

    def create_segment(self, seq):
        """Create a new :py:class:`hl7.Segment` compatible with this message"""
        return self.factory.create_segment(self.separators[1], seq, esc=self.esc, separators=self.separators[1:], factory=self.factory)

    def create_field(self, seq):
        """Create a new :py:class:`hl7.Field` compatible with this message"""
        return self.factory.create_field(self.separators[2], seq, esc=self.esc, separators=self.separators[2:], factory=self.factory)

    def create_repetition(self, seq):
        """Create a new :py:class:`hl7.Repetition` compatible with this message"""
        return self.factory.create_repetition(self.separators[3], seq, esc=self.esc, separators=self.separators[3:], factory=self.factory)

    def create_component(self, seq):
        """Create a new :py:class:`hl7.Component` compatible with this message"""
        return self.factory.create_component(self.separators[4], seq, esc=self.esc, separators=self.separators[4:], factory=self.factory)

    def create_ack(self, ack_code='AA', message_id=None, application=None, facility=None):
        """
        Create an hl7 ACK response :py:class:`hl7.Message`, per spec 2.9.2, for this message.

        See http://www.hl7standards.com/blog/2007/02/01/ack-message-original-mode-acknowledgement/

        ``ack_code`` options are one of `AA` (accept), `AR` (reject), `AE` (error)
        (see HL7 Table 0008 - Acknowledgment Code)
        ``message_id`` control message ID for ACK, defaults to unique generated ID
        ``application`` name of sending application, defaults to receiving application of message
        ``facility`` name of sending facility, defaults to receiving facility of message
        """
        source_msh = self.segment('MSH')
        msh = self.create_segment([self.create_field(['MSH'])])
        msa = self.create_segment([self.create_field(['MSA'])])
        ack = self.create_message([msh, msa])

        ack.assign_field(six.text_type(source_msh(1)), 'MSH', 1, 1)
        ack.assign_field(six.text_type(source_msh(2)), 'MSH', 1, 2)
        # Sending application is source receving application
        ack.assign_field(six.text_type(application) if application is not None else six.text_type(source_msh(5)), 'MSH', 1, 3)
        # Sending facility is source receving facility
        ack.assign_field(six.text_type(facility) if facility is not None else six.text_type(source_msh(6)), 'MSH', 1, 4)
        # Receiving application is source sending application
        ack.assign_field(six.text_type(source_msh(3)), 'MSH', 1, 5)
        # Receiving facility is source sending facility
        ack.assign_field(six.text_type(source_msh(4)), 'MSH', 1, 6)
        ack.assign_field(six.text_type(datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")), 'MSH', 1, 7)
        # Message type code
        ack.assign_field('ACK', 'MSH', 1, 9, 1, 1)
        # Copy trigger event from source
        ack.assign_field(six.text_type(source_msh(9)(1)(2)), 'MSH', 1, 9, 1, 2)
        ack.assign_field(message_id if message_id is not None else generate_message_control_id(), 'MSH', 1, 10)
        ack.assign_field(six.text_type(source_msh(11)), 'MSH', 1, 11)
        ack.assign_field(six.text_type(source_msh(12)), 'MSH', 1, 12)

        ack.assign_field(six.text_type(ack_code), 'MSA', 1, 1)
        ack.assign_field(six.text_type(source_msh(10)), 'MSA', 1, 2)

        return ack


@python_2_unicode_compatible
class Segment(Container):
    """Second level of an HL7 message, which represents an HL7 Segment.
    Traditionally this is a line of a message that ends with a carriage
    return and is separated by pipes. It contains a list of
    :py:class:`hl7.Field` instances.
    """
    def _adjust_index(self, index):
        # First element is the segment name, so we don't need to adjust to get 1-based
        return index

    def __str__(self):
        if six.text_type(self[0]) in ['MSH', 'FHS']:
            return six.text_type(self[0]) + six.text_type(self[1]) + six.text_type(self[2]) + six.text_type(self[1]) + \
                self.separator.join((six.text_type(x) for x in self[3:]))
        return self.separator.join((six.text_type(x) for x in self))


class Field(Container):
    """Third level of an HL7 message, that traditionally is surrounded
    by pipes and separated by carets. It contains a list of strings
    or :py:class:`hl7.Repetition` instances.
    """


class Repetition(Container):
    """Fourth level of an HL7 message. A field can repeat.
    It contains a list of strings or :py:class:`hl7.Component` instances.
    """


class Component(Container):
    """Fifth level of an HL7 message. A component is a composite datatypes.
    It contains a list of string sub-components.
    """


class Factory(object):
    """Factory used to create each type of Container.

    A subclass can be used to create specialized subclasses of each container.
    """
    create_message = Message        #: Create an instance of :py:class:`hl7.Message`
    create_segment = Segment        #: Create an instance of :py:class:`hl7.Segment`
    create_field = Field            #: Create an instance of :py:class:`hl7.Field`
    create_repetition = Repetition  #: Create an instance of :py:class:`hl7.Repetition`
    create_component = Component    #: Create an instance of :py:class:`hl7.Component`
