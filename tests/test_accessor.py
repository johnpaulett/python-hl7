# -*- coding: utf-8 -*-
from unittest import TestCase

from hl7 import Accessor, Field, Message, Segment


class AccessorTest(TestCase):
    def test_key(self):
        self.assertEqual("FOO", Accessor("FOO").key)
        self.assertEqual("FOO2", Accessor("FOO", 2).key)
        self.assertEqual("FOO2.3", Accessor("FOO", 2, 3).key)
        self.assertEqual("FOO2.3.1.4.6", Accessor("FOO", 2, 3, 1, 4, 6).key)
        self.assertEqual("FOO*", Accessor("FOO*").key)
        self.assertEqual("FOO2.3.*.4", Accessor("FOO", 2, 3, Accessor.WILDCARD, 4).key)
        self.assertEqual(
            "FOO*.3.*.4",
            Accessor("FOO", Accessor.WILDCARD, 3, Accessor.WILDCARD, 4).key,
        )
        with self.assertRaises(ValueError) as cm:
            Accessor("FOO", 1, Accessor.WILDCARD, 1)
        self.assertIn(
            "wildcard only supported for segment and repeat", cm.exception.args[0]
        )

    def test_parse(self):
        self.assertEqual(Accessor("FOO"), Accessor.parse_key("FOO"))
        self.assertEqual(
            Accessor("FOO", 2, 3, 1, 4, 6), Accessor.parse_key("FOO2.3.1.4.6")
        )
        self.assertEqual(
            Accessor("FOO", Accessor.WILDCARD, 3, Accessor.WILDCARD, 4, 6),
            Accessor.parse_key("FOO*.3.*.4.6"),
        )
        with self.assertRaises(ValueError) as cm:
            Accessor.parse_key("FOO.*.1")
        self.assertIn("wildcard not supported for F", cm.exception.args[0])

    def test_equality(self):
        self.assertEqual(Accessor("FOO", 1, 3, 4), Accessor("FOO", 1, 3, 4))
        self.assertNotEqual(Accessor("FOO", 1), Accessor("FOO", 2))

    def test_string(self):
        SEP = "|^~\\&"
        CR_SEP = "\r"
        MSH = Segment(SEP[0], [Field(SEP[2], ["MSH"])])
        MSA = Segment(SEP[0], [Field(SEP[2], ["MSA"])])
        response = Message(CR_SEP, [MSH, MSA])
        response["MSH.F1.R1"] = SEP[0]
        response["MSH.F2.R1"] = SEP[1:]
        self.assertEqual(str(response), "MSH|^~\\&|\rMSA\r")

        response["MSH.F9.R1.C1"] = "ORU"
        response["MSH.F9.R1.C2"] = "R01"
        response["MSH.F9.R1.C3"] = ""
        response["MSH.F12.R1"] = "2.4"
        response["MSA.F1.R1"] = "AA"
        response["MSA.F3.R1"] = "Application Message"
        self.assertEqual(
            str(response),
            "MSH|^~\\&|||||||ORU^R01^|||2.4\rMSA|AA||Application Message\r",
        )
