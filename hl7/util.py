# -*- coding: utf-8 -*-
import logging
import string
from uuid import uuid4

logger = logging.getLogger(__file__)


def ishl7(line):
    """Determines whether a *line* looks like an HL7 message.
    This method only does a cursory check and does not fully
    validate the message.

    :rtype: bool
    """
    # Prevent issues if the line is empty
    return line and (line.strip()[:3] in ["MSH"]) or False


def isfile(line):
    """
        Files are wrapped in FHS / FTS
        FHS = file header segment
        FTS = file trailer segment
    """
    return line and (line.strip()[:3] in ["FHS"]) or False


def split_file(hl7file):
    """
        Given a file, split out the messages.
        Does not do any validation on the message.
        Throws away batch and file segments.
    """
    rv = []
    for line in hl7file.split("\r"):
        line = line.strip()
        if line[:3] in ["FHS", "BHS", "FTS", "BTS"]:
            continue
        if line[:3] == "MSH":
            newmsg = [line]
            rv.append(newmsg)
        else:
            if len(rv) == 0:
                logger.error("Segment received before message header [%s]", line)
                continue
            rv[-1].append(line)
    rv = ["\r".join(msg) for msg in rv]
    for i, msg in enumerate(rv):
        if not msg[-1] == "\r":
            rv[i] = msg + "\r"
    return rv


alphanumerics = string.ascii_uppercase + string.digits


def generate_message_control_id():
    """Generate a 32 character uuid hex message id.
    """
    return uuid4().hex
