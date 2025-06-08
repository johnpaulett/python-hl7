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

    def test_parse_tzname(self):
        dt = parse_datetime("201403111412-0500")
        self.assertEqual("-0500", dt.tzname())
        dt = parse_datetime("201403111412+0530")
        self.assertEqual("+0530", dt.tzname())

    def test_utc_offset_float(self):
        self.assertEqual("-0500", _UTCOffset(-300.0).tzname(datetime.utcnow()))
        self.assertEqual("+0530", _UTCOffset(330.0).tzname(datetime.utcnow()))

    def test_parse_negative_zero_offset(self):
        dt = parse_datetime("201403111412-0030")
        self.assertEqual(dt.tzinfo, _UTCOffset(-30))

    def test_utcoffset_equality(self):
        self.assertEqual(_UTCOffset(60), _UTCOffset(60))
        self.assertNotEqual(_UTCOffset(60), _UTCOffset(-60))
        self.assertNotEqual(_UTCOffset(60), 60)

    def test_utcoffset_hash(self):
        a = _UTCOffset(45)
        b = _UTCOffset(45)
        self.assertEqual(hash(a), hash(b))
        self.assertEqual(len({a, b}), 1)
