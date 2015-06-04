# -*- coding: utf-8 -*-
"""python-hl7 is a simple library for parsing messages of Health Level 7
(HL7) version 2.x into Python objects.

* Documentation: http://python-hl7.readthedocs.org
* Source Code: http://github.com/johnpaulett/python-hl7
"""
from .version import get_version

__version__ = get_version()
__author__ = 'John Paulett'
__email__ = 'john -at- paulett.org'
__license__ = 'BSD'
__copyright__ = 'Copyright 2011, John Paulett <john -at- paulett.org>'

#: This is the HL7 Null value. It means that a field is present and blank.
NULL = '""'

from .parser import parse
from .containers import Sequence, Container, Message, Segment, Field, Repetition, Component, Factory
from .accessor import Accessor
from .util import ishl7, isfile, split_file, generate_message_control_id
from .datatypes import parse_datetime

__all__ = [
    "parse",
    "Sequence", "Container", "Message", "Segment", "Field", "Repetition", "Component", "Factory",
    "Accessor",
    "ishl7", "isfile", "split_file", "generate_message_control_id",
    "parse_datetime",
]
