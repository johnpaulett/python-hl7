# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import string
import datetime
import random
import logging

logger = logging.getLogger(__file__)


def ishl7(line):
    """Determines whether a *line* looks like an HL7 message.
    This method only does a cursory check and does not fully
    validate the message.

    :rtype: bool
    """
    # Prevent issues if the line is empty
    return line and (line.strip()[:3] in ['MSH']) or False


def isfile(line):
    """
        Files are wrapped in FHS / FTS
        FHS = file header segment
        FTS = file trailer segment
    """
    return line and (line.strip()[:3] in ['FHS']) or False


def split_file(hl7file):
    """
        Given a file, split out the messages.
        Does not do any validation on the message.
        Throws away batch and file segments.
    """
    rv = []
    for line in hl7file.split('\r'):
        line = line.strip()
        if line[:3] in ['FHS', 'BHS', 'FTS', 'BTS']:
            continue
        if line[:3] == 'MSH':
            newmsg = [line]
            rv.append(newmsg)
        else:
            if len(rv) == 0:
                logger.error('Segment received before message header [%s]', line)
                continue
            rv[-1].append(line)
    rv = ['\r'.join(msg) for msg in rv]
    for i, msg in enumerate(rv):
        if not msg[-1] == '\r':
            rv[i] = msg + '\r'
    return rv


alphanumerics = string.ascii_uppercase + string.digits


def generate_message_control_id():
    """Generate a unique 20 character message id.

    See http://www.hl7resources.com/Public/index.html?a55433.htm
    """
    d = datetime.datetime.utcnow()
    # Strip off the decade, ID only has to be unique for 3 years.
    # So now we have a 16 char timestamp.
    timestamp = d.strftime("%y%j%H%M%S%f")[1:]
    # Add 4 chars of uniqueness
    unique = ''.join(random.sample(alphanumerics, 4))
    return timestamp + unique
