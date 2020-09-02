# -*- coding: utf-8 -*-
from unittest import TestCase

import hl7
from hl7 import Field, Segment

from .samples import sample_hl7


class ContainerTest(TestCase):
    def test_unicode(self):
        msg = hl7.parse(sample_hl7)
        self.assertEqual(str(msg), sample_hl7)
        self.assertEqual(
            str(msg[3][3]), "1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN"
        )

    def test_container_unicode(self):
        c = hl7.Container("|")
        c.extend(["1", "b", "data"])
        self.assertEqual(str(c), "1|b|data")


class MessageTest(TestCase):
    def test_segments(self):
        msg = hl7.parse(sample_hl7)
        s = msg.segments("OBX")
        self.assertEqual(len(s), 2)
        self.assertIsInstance(s[0], Segment)
        self.assertEqual(s[0][0:3], [["OBX"], ["1"], ["SN"]])
        self.assertEqual(s[1][0:3], [["OBX"], ["2"], ["FN"]])

        self.assertIsInstance(s[0][1], Field)

    def test_segments_does_not_exist(self):
        msg = hl7.parse(sample_hl7)
        self.assertRaises(KeyError, msg.segments, "BAD")

    def test_segment(self):
        msg = hl7.parse(sample_hl7)
        s = msg.segment("OBX")
        self.assertEqual(s[0:3], [["OBX"], ["1"], ["SN"]])

    def test_segment_does_not_exist(self):
        msg = hl7.parse(sample_hl7)
        self.assertRaises(KeyError, msg.segment, "BAD")

    def test_segments_dict_key(self):
        msg = hl7.parse(sample_hl7)
        s = msg["OBX"]
        self.assertEqual(len(s), 2)
        self.assertEqual(s[0][0:3], [["OBX"], ["1"], ["SN"]])
        self.assertEqual(s[1][0:3], [["OBX"], ["2"], ["FN"]])

    def test_MSH_1_field(self):
        msg = hl7.parse(sample_hl7)
        f = msg["MSH.1"]
        self.assertEqual(len(f), 1)
        self.assertEqual(f, "|")

    def test_MSH_2_field(self):
        msg = hl7.parse(sample_hl7)
        f = msg["MSH.2"]
        self.assertEqual(len(f), 4)
        self.assertEqual(f, "^~\\&")

    def test_get_slice(self):
        msg = hl7.parse(sample_hl7)
        s = msg.segments("OBX")[0]
        self.assertIsInstance(s, Segment)
        self.assertIsInstance(s[0:3], Segment)

    def test_ack(self):
        msg = hl7.parse(sample_hl7)
        ack = msg.create_ack()
        self.assertEqual(msg["MSH.1"], ack["MSH.1"])
        self.assertEqual(msg["MSH.2"], ack["MSH.2"])
        self.assertEqual("ACK", ack["MSH.9.1.1"])
        self.assertEqual(msg["MSH.9.1.2"], ack["MSH.9.1.2"])
        self.assertEqual("ACK", ack["MSH.9.1.3"])
        self.assertNotEqual(msg["MSH.7"], ack["MSH.7"])
        self.assertNotEqual(msg["MSH.10"], ack["MSH.10"])
        self.assertEqual("AA", ack["MSA.1"])
        self.assertEqual(msg["MSH.10"], ack["MSA.2"])
        self.assertEqual(20, len(ack["MSH.10"]))
        self.assertEqual(msg["MSH.5"], ack["MSH.3"])
        self.assertEqual(msg["MSH.6"], ack["MSH.4"])
        self.assertEqual(msg["MSH.3"], ack["MSH.5"])
        self.assertEqual(msg["MSH.4"], ack["MSH.6"])
        ack2 = msg.create_ack(
            ack_code="AE", message_id="testid", application="python", facility="test"
        )
        self.assertEqual("AE", ack2["MSA.1"])
        self.assertEqual("testid", ack2["MSH.10"])
        self.assertEqual("python", ack2["MSH.3"])
        self.assertEqual("test", ack2["MSH.4"])
        self.assertNotEqual(ack["MSH.10"], ack2["MSH.10"])


class TestMessage(hl7.Message):
    pass


class TestSegment(hl7.Segment):
    pass


class TestField(hl7.Field):
    pass


class TestRepetition(hl7.Repetition):
    pass


class TestComponent(hl7.Component):
    pass


class TestFactory(hl7.Factory):
    create_message = TestMessage
    create_segment = TestSegment
    create_field = TestField
    create_repetition = TestRepetition
    create_component = TestComponent


class FactoryTest(TestCase):
    def test_parse(self):
        msg = hl7.parse(sample_hl7, factory=TestFactory)
        self.assertIsInstance(msg, TestMessage)
        s = msg.segments("OBX")
        self.assertIsInstance(s[0], TestSegment)
        self.assertIsInstance(s[0](3), TestField)
        self.assertIsInstance(s[0](3)(1), TestRepetition)
        self.assertIsInstance(s[0](3)(1)(1), TestComponent)
        self.assertEqual("1554-5", s[0](3)(1)(1)(1))

    def test_ack(self):
        msg = hl7.parse(sample_hl7, factory=TestFactory)
        ack = msg.create_ack()
        self.assertIsInstance(ack, TestMessage)
        self.assertIsInstance(ack(1)(9), TestField)
        self.assertIsInstance(ack(1)(9)(1), TestRepetition)
        self.assertIsInstance(ack(1)(9)(1)(2), TestComponent)
        self.assertEqual("R01", ack(1)(9)(1)(2)(1))
