# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import six
from .containers import Factory


def parse(line, encoding='utf-8', factory=Factory):
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
    if isinstance(line, six.binary_type):
        line = line.decode(encoding)
    # Strip out unnecessary whitespace
    strmsg = line.strip()
    # The method for parsing the message
    plan = create_parse_plan(strmsg, factory)
    # Start spliting the methods based upon the ParsePlan
    return _split(strmsg, plan)


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
    if plan.containers[0] == plan.factory.create_segment and text[:3] in ['MSH', 'FHS']:
        seg = text[:3]
        sep0 = text[3]
        sep_end_off = text.find(sep0, 4)
        seps = text[4:sep_end_off]
        text = text[sep_end_off + 1:]
        data = [plan.factory.create_field('', [seg]), plan.factory.create_field('', [sep0]), plan.factory.create_field(sep0, [seps])]
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
    separators = ['\r']

    # Extract the rest of the separators. Defaults used if not present.
    assert strmsg[:3] in ('MSH')
    sep0 = strmsg[3]
    seps = list(strmsg[3: strmsg.find(sep0, 4)])

    separators.append(seps[0])
    if len(seps) > 2:
        separators.append(seps[2])   # repetition separator
    else:
        separators.append('~')       # repetition separator
    if len(seps) > 1:
        separators.append(seps[1])   # component separator
    else:
        separators.append('^')       # component separator
    if len(seps) > 4:
        separators.append(seps[4])   # sub-component separator
    else:
        separators.append('&')       # sub-component separator
    if len(seps) > 3:
        esc = seps[3]
    else:
        esc = '\\'

    # The ordered list of containers to create
    containers = [factory.create_message, factory.create_segment, factory.create_field, factory.create_repetition, factory.create_component]
    return _ParsePlan(separators, containers, esc, factory)


class _ParsePlan(object):
    """Details on how to parse an HL7 message. Typically this object
    should be created via :func:`hl7.create_parse_plan`
    """
    # field, component, repetition, escape, subcomponent

    def __init__(self, separators, containers, esc, factory):
        # TODO test to see performance implications of the assertion
        # since we generate the ParsePlan, this should never be in
        # invalid state
        assert len(containers) == len(separators)
        self.separators = separators
        self.containers = containers
        self.esc = esc
        self.factory = factory

    @property
    def separator(self):
        """Return the current separator to use based on the plan."""
        return self.separators[0]

    def container(self, data):
        """Return an instance of the approriate container for the *data*
        as specified by the current plan.
        """
        return self.containers[0](self.separator, data, self.esc, self.separators, self.factory)

    def next(self):
        """Generate the next level of the plan (essentially generates
        a copy of this plan with the level of the container and the
        seperator starting at the next index.
        """
        if len(self.containers) > 1:
            # Return a new instance of this class using the tails of
            # the separators and containers lists. Use self.__class__()
            # in case :class:`hl7.ParsePlan` is subclassed
            return self.__class__(self.separators[1:], self.containers[1:], self.esc, self.factory)
        # When we have no separators and containers left, return None,
        # which indicates that we have nothing further.
        return None

    def applies(self, text):
        """return True if the separator or those if the children are in the text"""
        for s in self.separators:
            if text.find(s) >= 0:
                return True
        return False
