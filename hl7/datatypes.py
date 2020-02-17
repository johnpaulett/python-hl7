# -*- coding: utf-8 -*-
import datetime
import math
import re

DTM_TZ_RE = re.compile(r"(\d+(?:\.\d+)?)(?:([+-]\d{2})(\d{2}))?")


class _UTCOffset(datetime.tzinfo):
    """Fixed offset timezone from UTC."""

    def __init__(self, minutes):
        """``minutes`` is a offset from UTC, negative for west of UTC"""
        self.minutes = minutes

    def utcoffset(self, dt):
        return datetime.timedelta(minutes=self.minutes)

    def tzname(self, dt):
        minutes = abs(self.minutes)
        return "{0}{1:02}{2:02}".format(
            "-" if self.minutes < 0 else "+", minutes // 60, minutes % 60
        )

    def dst(self, dt):
        return datetime.timedelta(0)


def parse_datetime(value):
    """Parse hl7 DTM string ``value`` :py:class:`datetime.datetime`.

    ``value`` is of the format YYYY[MM[DD[HH[MM[SS[.S[S[S[S]]]]]]]]][+/-HHMM]
    or a ValueError will be raised.

    :rtype: :py:;class:`datetime.datetime`
    """
    if not value:
        return None

    # Split off optional timezone
    dt_match = DTM_TZ_RE.match(value)
    if not dt_match:
        raise ValueError("Malformed HL7 datetime {0}".format(value))
    dtm = dt_match.group(1)
    tzh = dt_match.group(2)
    tzm = dt_match.group(3)
    if tzh and tzm:
        minutes = int(tzh) * 60
        minutes += math.copysign(int(tzm), minutes)
        tzinfo = _UTCOffset(minutes)
    else:
        tzinfo = None

    precision = len(dtm)

    if precision >= 4:
        year = int(dtm[0:4])
    else:
        raise ValueError("Malformed HL7 datetime {0}".format(value))

    if precision >= 6:
        month = int(dtm[4:6])
    else:
        month = 1

    if precision >= 8:
        day = int(dtm[6:8])
    else:
        day = 1

    if precision >= 10:
        hour = int(dtm[8:10])
    else:
        hour = 0

    if precision >= 12:
        minute = int(dtm[10:12])
    else:
        minute = 0

    if precision >= 14:
        delta = datetime.timedelta(seconds=float(dtm[12:]))
        second = delta.seconds
        microsecond = delta.microseconds
    else:
        second = 0
        microsecond = 0

    return datetime.datetime(
        year, month, day, hour, minute, second, microsecond, tzinfo=tzinfo
    )
