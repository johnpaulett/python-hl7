# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 John Paulett (john -at- 7oars.com)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

"""Simple library for parsing messages of Health Level 7 (HL7)
version 2.x. 

HL7 is a communication protocol and message format for 
health care data. It is the de facto standard for transmitting data
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

As an example, let's create a HL7 message:

>>> message = 'MSH|^~\&|GHH LAB|ELAB-3|GHH OE|BLDG4|200202150930||ORU^R01|CNTRL-3456|P|2.4\r'
>>> message += 'PID|||555-44-4444||EVERYWOMAN^EVE^E^^^^L|JONES|196203520|F|||153 FERNWOOD DR.^^STATESVILLE^OH^35292||(206)3345232|(206)752-121||||AC555444444||67-A4335^OH^20030520\r'
>>> message += 'OBR|1|845439^GHH OE|1045813^GHH LAB|1554-5^GLUCOSE|||200202150730||||||||555-55-5555^PRIMARY^PATRICIA P^^^^MD^^LEVEL SEVEN HEALTHCARE, INC.|||||||||F||||||444-44-4444^HIPPOCRATES^HOWARD H^^^^MD\r'
>>> message += 'OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F\r
'
We call the hl7.parse() command with string message:

>>> h = parse(message)

We get a n-dimensional list back:

>>> type(h)
<type 'list'>

There were 4 segments (MSH, PID, OBR, OBX):

>>> len(h)
4

We can extract individual elements of the message:

>>> h[3][3][1]
'GLUCOSE'
>>> h[3][5][1]
'182'

We can look up segments by the segment identifer:

>>> pid = segment('PID', h)
>>> pid[3][0]
'555-44-4444'


Project site: http://www.bitbucket.org/johnpaulett/python-hl7/wiki/Home

HL7 References:
 * http://en.wikipedia.org/wiki/HL7
 * http://nule.org/wp/?page_id=99
 * http://www.hl7.org/
"""

__version__ = '0.0.3'
__author__ = 'John Paulett'
__email__ = 'john -at- 7oars.com'
__license__ = 'BSD'
__copyright__ = 'Copyright 2009, John Paulett <john -at- 7oars.com>'
__url__ = 'http://www.bitbucket.org/johnpaulett/python-hl7/wiki/Home'

def ishl7(line):
    """Determines whether a *line* looks like an HL7 message.
    This method only does a cursory check and does not fully 
    validate the message.
    """
    ## Prevent issues if the line is empty
    return line.strip().startswith('MSH') if line else False

def segment(segment_id, message):
    """Gets the first segment with the *segment_id* from the parsed *message*.

    >>> segment('OBX', [[['OBR'],['1']], [['OBX'], ['1']], [['OBX'], ['2']]])
    [['OBX'], ['1']]
    """
    ## Get the list of all the segments and pull out the first one if possible
    match = segments(segment_id, message)
    ## Make sure we won't get an IndexError
    return match[0] if match else None
    
def segments(segment_id, message):
    """Returns the requested segments from the parsed *message* that are identified
    by the *segment_id* (e.g. OBR, MSH, ORC, OBX).
    
    >>> segments('OBX', [[['OBR'], ['1']], [['OBX'], ['1']], [['OBX'], ['2']]])
    [[['OBX'], ['1']], [['OBX'], ['2']]]
    """
    ## Compare segment_id to the very first string in each segment, returning
    ## all segments that match
    return [segment for segment in message if segment[0][0] == segment_id]
    
def parse(line, delims = ('\r','|','^')):
    """Returns a n-dimensional list of the HL7 message that allows indexed 
    access of the elements (``n = len(delims)``).
    
    >>> parse('a|b^4|c\re|f|')
    [[['a'], ['b', '4'], ['c']], [['e'], ['f'], ['']]]
    """
    ## We make delims' default an immutable tuple to avoid issues of a 
    ## mutable default parameter
    return _split(line.strip(), delims)

def _split(text, delims):
    """Recursive function to split the *text* into an n-deep list, where 
    ``n = len(delims)``. 
    """
    ## Base condition, if we have used up all the delimiters
    if not delims:
        return text
    
    ## Recurse so that the delims are used in order to split the data
    ## into sub-lists.
    return [_split(x, delims[1:]) for x in text.split(delims[0])]

