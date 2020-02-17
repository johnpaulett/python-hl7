from datetime import datetime
from unittest import TestCase

from hl7.datatypes import _UTCOffset, parse_datetime


class DatetimeTest(TestCase):
    def test_parse_date(self):
        self.assertEqual(datetime(1901, 2, 13), parse_datetime("19010213"))

    def test_parse_datetime(self):
        self.assertEqual(
            datetime(2014, 3, 11, 14, 25, 33), parse_datetime("20140311142533")
        )

    def test_parse_datetime_frac(self):
        self.assertEqual(
            datetime(2014, 3, 11, 14, 25, 33, 100000),
            parse_datetime("20140311142533.1"),
        )
        self.assertEqual(
            datetime(2014, 3, 11, 14, 25, 33, 10000),
            parse_datetime("20140311142533.01"),
        )
        self.assertEqual(
            datetime(2014, 3, 11, 14, 25, 33, 1000),
            parse_datetime("20140311142533.001"),
        )
        self.assertEqual(
            datetime(2014, 3, 11, 14, 25, 33, 100),
            parse_datetime("20140311142533.0001"),
        )

    def test_parse_tz(self):
        self.assertEqual(
            datetime(2014, 3, 11, 14, 12, tzinfo=_UTCOffset(330)),
            parse_datetime("201403111412+0530"),
        )
        self.assertEqual(
            datetime(2014, 3, 11, 14, 12, 20, tzinfo=_UTCOffset(-300)),
            parse_datetime("20140311141220-0500"),
        )

    def test_tz(self):
        self.assertEqual("+0205", _UTCOffset(125).tzname(datetime.utcnow()))
        self.assertEqual("-0410", _UTCOffset(-250).tzname(datetime.utcnow()))
