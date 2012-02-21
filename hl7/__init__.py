# -*- coding: utf-8 -*-
"""python-hl7 is a simple library for parsing messages of Health Level 7 
(HL7) version 2.x into Python objects.

* Documentation: http://python-hl7.readthedocs.org
* Source Code: http://github.com/johnpaulett/python-hl7
"""

__version__ = '0.2.4'
__author__ = 'John Paulett'
__email__ = 'john -at- paulett.org'
__license__ = 'BSD'
__copyright__ = 'Copyright 2011, John Paulett <john -at- paulett.org>'
__url__ = 'http://python-hl7.readthedocs.org'

def ishl7(line):
    """Determines whether a *line* looks like an HL7 message.
    This method only does a cursory check and does not fully 
    validate the message.

    :rtype: bool
    """
    ## Prevent issues if the line is empty
    return line.strip().startswith('MSH') if line else False

def parse(line):
    """Returns a instance of the :py:class:`hl7.Message` that allows
    indexed access to the data elements.

    .. note::

        HL7 usually contains only ASCII, but can use other character
        sets (HL7 Standards Document, Section 1.7.1). Therefore,
        python-hl7 works on Python unicode strings. :py:func:`hl7.parse`
        will accept ASCII-only strings and automatically convert them
        into unicode.  However, if the message contains non-ASCII
        characters, it is the responsibility of the caller of
        :py:func:`hl7.parse` to properly convert the message string
        to unicode first.

    >>> h = hl7.parse(message)

    :rtype: :py:class:`hl7.Message`
    """
    ## ensure that we get unicode input. For regular ASCII, the conversion
    ## will occur seamlessly, but for non-ASCII strings, parse must receive
    ## a unicode string or it will error out
    line = unicode(line)
    ## Strip out unnecessary whitespace
    strmsg = line.strip()
    ## The method for parsing the message
    plan = create_parse_plan(strmsg)
    ## Start spliting the methods based upon the ParsePlan
    return _split(strmsg, plan)

def _split(text, plan):
    """Recursive function to split the *text* into an n-deep list,
    according to the :py:class:`hl7._ParsePlan`.
    """
    ## Base condition, if we have used up all the plans
    if not plan:
        return text

    ## Recurse so that the sub plans are used in order to split the data
    ## into the approriate type as defined by the current plan.
    data = [_split(x, plan.next()) for x in text.split(plan.separator)]
    ## Return the instance of the current message part according
    ## to the plan
    return plan.container(data)

class Container(list):
    """Abstract root class for the parts of the HL7 message."""
    def __init__(self, separator, sequence=[]):
        ## Initialize the list object, optionally passing in the
        ## sequence.  Since list([]) == [], using the default
        ## parameter will not cause any issues.
        super(Container, self).__init__(sequence)
        self.separator = separator

    def __unicode__(self):
        """Join a the child containers into a single string, separated
        by the self.separator.  This method acts recursively, calling
        the children's __unicode__ method.  Thus ``unicode()`` is the
        approriate method for turning the python-hl7 representation of
        HL7 into a standard string.

        >>> unicode(h) == message
        True

        """
        return self.separator.join((unicode(x) for x in self))

class Message(Container):
    """Representation of an HL7 message. It contains a list
    of :py:class:`hl7.Segment` instances.
    """

    def __getitem__(self, key):
        """Index or segment-based lookup.

        If key is an integer, ``__getitem__`` acts list a list, returning
        the :py:class:`hl7.Segment` held at that index:

        >>> h[1]
        [[u'PID'], ...]

        If the key is a string, ``__getitem__`` acts like a dictionary,
        returning all segments whose *segment_id* is *key*
        (alias of :py:meth:`hl7.Message.segments`).

        >>> h['OBX']
        [[[u'OBX'], [u'1'], ...]]

        :rtype: :py:class:`hl7.Segment` or list of :py:class:`hl7.Segment`
        """
        if isinstance(key, basestring):
            return self.segments(key)
        return list.__getitem__(self, key)

    def segment(self, segment_id):
        """Gets the first segment with the *segment_id* from the parsed
        *message*.

        >>> h.segment('PID')
        [[u'PID'], ...]

        :rtype: :py:class:`hl7.Segment`
        """
        ## Get the list of all the segments and pull out the first one,
        ## if possible
        match = self.segments(segment_id)
        ## We should never get an IndexError, since segments will instead
        ## throw an KeyError
        return match[0]

    def segments(self, segment_id):
        """Returns the requested segments from the parsed *message* that are
        identified by the *segment_id* (e.g. OBR, MSH, ORC, OBX).

        >>> h.segments('OBX')
        [[[u'OBX'], [u'1'], ...]]

        :rtype: list of :py:class:`hl7.Segment`
        """
        ## Compare segment_id to the very first string in each segment,
        ## returning all segments that match
        matches = [segment for segment in self if segment[0][0] == segment_id]
        if len(matches) == 0:
            raise KeyError('No %s segments' % segment_id)
        return matches

class Segment(Container):
    """Second level of an HL7 message, which represents an HL7 Segment.
    Traditionally this is a line of a message that ends with a carriage
    return and is separated by pipes. It contains a list of
    :py:class:`hl7.Field` instances.
    """

class Field(Container):
    """Third level of an HL7 message, that traditionally is surrounded
    by pipes and separated by carets. It contains a list of strings.
    """

def create_parse_plan(strmsg):
    """Creates a plan on how to parse the HL7 message according to
    the details stored within the message.
    """
    ## We will always use a carriage return to separate segments
    separators = ['\r']
    ## Parse out the other separators from the characters following
    ## MSH.  Currently we only go two-levels deep and ignore some
    ## details.
    separators.extend(list(strmsg[3:5]))
    ## The ordered list of containers to create
    containers = [Message, Segment, Field]
    return _ParsePlan(separators, containers)

class _ParsePlan(object):
    """Details on how to parse an HL7 message. Typically this object
    should be created via :func:`hl7.create_parse_plan`
    """
    # field, component, repetition, escape, subcomponent
    # TODO implement escape, and subcomponent

    def __init__(self, separators, containers):
        # TODO test to see performance implications of the assertion
        # since we generate the ParsePlan, this should never be in
        # invalid state
        assert len(containers) == len(separators)
        self.separators = separators
        self.containers = containers

    @property
    def separator(self):
        """Return the current separator to use based on the plan."""
        return self.separators[0]

    def container(self, data):
        """Return an instance of the approriate container for the *data*
        as specified by the current plan.
        """
        return self.containers[0](self.separator, data)

    def next(self):
        """Generate the next level of the plan (essentially generates
        a copy of this plan with the level of the container and the
        seperator starting at the next index.
        """
        if len(self.containers) > 1:
            ## Return a new instance of this class using the tails of
            ## the separators and containers lists. Use self.__class__()
            ## in case :class:`hl7.ParsePlan` is subclassed
            return  self.__class__(self.separators[1:], self.containers[1:])
        ## When we have no separators and containers left, return None,
        ## which indicates that we have nothing further.
        return None
