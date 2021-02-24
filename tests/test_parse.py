# -*- coding: utf-8 -*-
from unittest import TestCase

import hl7
from hl7 import Accessor, Component, Field, Message, ParseException, Repetition, Segment

from .samples import (
    rep_sample_hl7,
    sample_bad_batch,
    sample_bad_batch1,
    sample_bad_file,
    sample_bad_file1,
    sample_bad_file2,
    sample_bad_file3,
    sample_batch,
    sample_batch1,
    sample_batch2,
    sample_batch3,
    sample_batch4,
    sample_file,
    sample_file1,
    sample_file2,
    sample_file3,
    sample_file4,
    sample_file5,
    sample_file6,
    sample_hl7,
)


class ParseTest(TestCase):
    def test_parse(self):
        msg = hl7.parse(sample_hl7)
        self.assertEqual(len(msg), 5)
        self.assertIsInstance(msg[0][0][0], str)
        self.assertEqual(msg[0][0][0], "MSH")
        self.assertEqual(msg[3][0][0], "OBX")
        self.assertEqual(
            msg[3][3],
            [[["1554-5"], ["GLUCOSE"], ["POST 12H CFST:MCNC:PT:SER/PLAS:QN"]]],
        )
        # Make sure MSH-1 and MSH-2 are valid
        self.assertEqual(msg[0][1][0], "|")
        self.assertIsInstance(msg[0][1], hl7.Field)
        self.assertEqual(msg[0][2][0], r"^~\&")
        self.assertIsInstance(msg[0][2], hl7.Field)
        # MSH-9 is the message type
        self.assertEqual(msg[0][9], [[["ORU"], ["R01"]]])
        # Do it twice to make sure text coercion is idempotent
        self.assertEqual(str(msg), sample_hl7)
        self.assertEqual(str(msg), sample_hl7)

    def test_parse_batch(self):
        batch = hl7.parse_batch(sample_batch)
        self.assertEqual(len(batch), 1)
        self.assertIsInstance(batch[0], hl7.Message)
        self.assertIsInstance(batch.header, hl7.Segment)
        self.assertEqual(batch.header[0][0], "BHS")
        self.assertEqual(batch.header[4][0], "ABCHS")
        self.assertIsInstance(batch.trailer, hl7.Segment)
        self.assertEqual(batch.trailer[0][0], "BTS")
        self.assertEqual(batch.trailer[1][0], "1")

    def test_parse_batch1(self):
        batch = hl7.parse_batch(sample_batch1)
        self.assertEqual(len(batch), 2)
        self.assertIsInstance(batch[0], hl7.Message)
        self.assertEqual(batch[0][0][10][0], "12334456778890")
        self.assertIsInstance(batch[1], hl7.Message)
        self.assertEqual(batch[1][0][10][0], "12334456778891")
        self.assertIsInstance(batch.header, hl7.Segment)
        self.assertEqual(batch.header[0][0], "BHS")
        self.assertEqual(batch.header[4][0], "ABCHS")
        self.assertIsInstance(batch.trailer, hl7.Segment)
        self.assertEqual(batch.trailer[0][0], "BTS")
        self.assertEqual(batch.trailer[1][0], "2")

    def test_parse_batch2(self):
        batch = hl7.parse_batch(sample_batch2)
        self.assertEqual(len(batch), 2)
        self.assertIsInstance(batch[0], hl7.Message)
        self.assertEqual(batch[0][0][10][0], "12334456778890")
        self.assertIsInstance(batch[1], hl7.Message)
        self.assertEqual(batch[1][0][10][0], "12334456778891")
        self.assertFalse(batch.header)
        self.assertFalse(batch.trailer)

    def test_parse_batch3(self):
        batch = hl7.parse_batch(sample_batch3)
        self.assertEqual(len(batch), 1)
        self.assertIsInstance(batch[0], hl7.Message)
        self.assertIsInstance(batch.header, hl7.Segment)
        self.assertEqual(batch.header[0][0], "BHS")
        self.assertEqual(batch.header[4][0], "ABCHS")
        self.assertIsInstance(batch.trailer, hl7.Segment)
        self.assertEqual(batch.trailer[0][0], "BTS")

    def test_parse_batch4(self):
        batch = hl7.parse_batch(sample_batch4)
        self.assertEqual(len(batch), 1)
        self.assertIsInstance(batch[0], hl7.Message)
        self.assertIsNone(batch.header)
        self.assertIsNone(batch.trailer)

    def test_parse_bad_batch(self):
        with self.assertRaises(ParseException) as cm:
            hl7.parse_batch(sample_bad_batch)
        self.assertIn("Segment received before message header", cm.exception.args[0])

    def test_parse_bad_batch1(self):
        with self.assertRaises(ParseException) as cm:
            hl7.parse_batch(sample_bad_batch1)
        self.assertIn(
            "Batch cannot have more than one BHS segment", cm.exception.args[0]
        )

    def test_parse_file(self):
        file = hl7.parse_file(sample_file)
        self.assertEqual(len(file), 1)
        self.assertIsInstance(file[0], hl7.Batch)
        self.assertIsInstance(file.header, hl7.Segment)
        self.assertEqual(file.header[0][0], "FHS")
        self.assertEqual(file.header[4][0], "ABCHS")
        self.assertIsInstance(file.trailer, hl7.Segment)
        self.assertEqual(file.trailer[0][0], "FTS")
        self.assertEqual(file.trailer[1][0], "1")

    def test_parse_file1(self):
        file = hl7.parse_file(sample_file1)
        self.assertEqual(len(file), 2)
        self.assertIsInstance(file[0], hl7.Batch)
        self.assertEqual(file[0].trailer[1][0], "2")
        self.assertIsInstance(file[1], hl7.Batch)
        self.assertEqual(file[1].trailer[1][0], "1")
        self.assertNotEqual(file[0], file[1])
        self.assertIsInstance(file.header, hl7.Segment)
        self.assertEqual(file.header[0][0], "FHS")
        self.assertEqual(file.header[4][0], "ABCHS")
        self.assertIsInstance(file.trailer, hl7.Segment)
        self.assertEqual(file.trailer[0][0], "FTS")
        self.assertEqual(file.trailer[1][0], "2")

    def test_parse_file2(self):
        file = hl7.parse_file(sample_file2)
        self.assertEqual(len(file), 1)
        self.assertIsInstance(file[0], hl7.Batch)
        self.assertIsInstance(file.header, hl7.Segment)
        self.assertEqual(file.header[0][0], "FHS")
        self.assertEqual(file.header[4][0], "ABCHS")
        self.assertIsInstance(file.trailer, hl7.Segment)
        self.assertEqual(file.trailer[0][0], "FTS")
        self.assertEqual(file.trailer[1][0], "1")

    def test_parse_file3(self):
        file = hl7.parse_file(sample_file3)
        self.assertEqual(len(file), 1)
        self.assertIsInstance(file[0], hl7.Batch)
        self.assertIsInstance(file.header, hl7.Segment)
        self.assertEqual(file.header[0][0], "FHS")
        self.assertEqual(file.header[4][0], "ABCHS")
        self.assertIsInstance(file.trailer, hl7.Segment)
        self.assertEqual(file.trailer[0][0], "FTS")

    def test_parse_file4(self):
        file = hl7.parse_file(sample_file4)
        self.assertEqual(len(file), 1)
        self.assertIsInstance(file[0], hl7.Batch)
        self.assertIsNone(file.header)
        self.assertIsNone(file.trailer)

    def test_parse_file5(self):
        file = hl7.parse_file(sample_file5)
        self.assertEqual(len(file), 1)
        self.assertIsInstance(file[0], hl7.Batch)
        self.assertIsInstance(file.header, hl7.Segment)
        self.assertEqual(file.header[0][0], "FHS")
        self.assertEqual(file.header[4][0], "ABCHS")
        self.assertIsInstance(file.trailer, hl7.Segment)
        self.assertEqual(file.trailer[0][0], "FTS")
        self.assertEqual(file.trailer[1][0], "1")

    def test_parse_file6(self):
        file = hl7.parse_file(sample_file6)
        self.assertEqual(len(file), 1)
        self.assertIsInstance(file[0], hl7.Batch)
        self.assertIsInstance(file.header, hl7.Segment)
        self.assertEqual(file.header[0][0], "FHS")
        self.assertEqual(file.header[4][0], "ABCHS")
        self.assertIsInstance(file.trailer, hl7.Segment)
        self.assertEqual(file.trailer[0][0], "FTS")
        self.assertEqual(file.trailer[1][0], "1")

    def test_parse_bad_file(self):
        with self.assertRaises(ParseException) as cm:
            hl7.parse_file(sample_bad_file)
        self.assertIn("Segment received before message header", cm.exception.args[0])

    def test_parse_bad_file1(self):
        with self.assertRaises(ParseException) as cm:
            hl7.parse_file(sample_bad_file1)
        self.assertIn(
            "Batch cannot have more than one BHS segment", cm.exception.args[0]
        )

    def test_parse_bad_file2(self):
        with self.assertRaises(ParseException) as cm:
            hl7.parse_file(sample_bad_file2)
        self.assertIn(
            "File cannot have more than one FHS segment", cm.exception.args[0]
        )

    def test_parse_bad_file3(self):
        with self.assertRaises(ParseException) as cm:
            hl7.parse_file(sample_bad_file3)
        self.assertIn("Segment received before message header", cm.exception.args[0])

    def test_parse_hl7(self):
        obj = hl7.parse_hl7(sample_hl7)
        self.assertIsInstance(obj, hl7.Message)
        obj = hl7.parse_hl7(sample_batch)
        self.assertIsInstance(obj, hl7.Batch)
        obj = hl7.parse_hl7(sample_batch1)
        self.assertIsInstance(obj, hl7.Batch)
        obj = hl7.parse_hl7(sample_batch2)
        self.assertIsInstance(obj, hl7.Batch)
        obj = hl7.parse_hl7(sample_file)
        self.assertIsInstance(obj, hl7.File)
        obj = hl7.parse_hl7(sample_file1)
        self.assertIsInstance(obj, hl7.File)
        obj = hl7.parse_hl7(sample_file2)
        self.assertIsInstance(obj, hl7.File)

    def test_bytestring_converted_to_unicode(self):
        msg = hl7.parse(str(sample_hl7))
        self.assertEqual(len(msg), 5)
        self.assertIsInstance(msg[0][0][0], str)
        self.assertEqual(msg[0][0][0], "MSH")

    def test_non_ascii_bytestring(self):
        # \x96 - valid cp1252, not valid utf8
        # it is the responsibility of the caller to convert to unicode
        msg = hl7.parse(b"MSH|^~\\&|GHH LAB|ELAB\x963", encoding="cp1252")
        self.assertEqual(msg[0][4][0], "ELAB\u20133")

    def test_non_ascii_bytestring_no_encoding(self):
        # \x96 - valid cp1252, not valid utf8
        # it is the responsibility of the caller to convert to unicode
        self.assertRaises(UnicodeDecodeError, hl7.parse, b"MSH|^~\\&|GHH LAB|ELAB\x963")

    def test_parsing_classes(self):
        msg = hl7.parse(sample_hl7)

        self.assertIsInstance(msg, hl7.Message)
        self.assertIsInstance(msg[3], hl7.Segment)
        self.assertIsInstance(msg[3][0], hl7.Field)
        self.assertIsInstance(msg[3][0][0], str)

    def test_nonstandard_separators(self):
        nonstd = "MSH$%~\\&$GHH LAB\rPID$$$555-44-4444$$EVERYWOMAN%EVE%E%%%L\r"
        msg = hl7.parse(nonstd)

        self.assertEqual(str(msg), nonstd)
        self.assertEqual(len(msg), 2)
        self.assertEqual(
            msg[1][5], [[["EVERYWOMAN"], ["EVE"], ["E"], [""], [""], ["L"]]]
        )

    def test_repetition(self):
        msg = hl7.parse(rep_sample_hl7)
        self.assertEqual(msg[1][4], [["Repeat1"], ["Repeat2"]])
        self.assertIsInstance(msg[1][4], Field)
        self.assertIsInstance(msg[1][4][0], Repetition)
        self.assertIsInstance(msg[1][4][1], Repetition)
        self.assertEqual(str(msg[1][4][0][0]), "Repeat1")
        self.assertIsInstance(msg[1][4][0][0], str)
        self.assertEqual(str(msg[1][4][1][0]), "Repeat2")
        self.assertIsInstance(msg[1][4][1][0], str)

    def test_empty_initial_repetition(self):
        # Switch to look like "|~Repeat2|
        msg = hl7.parse(rep_sample_hl7.replace("Repeat1", ""))
        self.assertEqual(msg[1][4], [[""], ["Repeat2"]])

    def test_subcomponent(self):
        msg = hl7.parse(rep_sample_hl7)
        self.assertEqual(
            msg[1][3],
            [[["Component1"], ["Sub-Component1", "Sub-Component2"], ["Component3"]]],
        )

    def test_elementnumbering(self):
        # Make sure that the numbering of repetitions. components and
        # sub-components is indexed from 1 when invoked as callable
        # (for compatibility with HL7 spec numbering)
        # and not 0-based (default for Python list)
        msg = hl7.parse(rep_sample_hl7)
        f = msg(2)(3)(1)(2)(2)
        self.assertIs(f, msg["PID.3.1.2.2"])
        self.assertIs(f, msg[1][3][0][1][1])
        f = msg(2)(4)(2)(1)
        self.assertIs(f, msg["PID.4.2.1"])
        self.assertIs(f, msg[1][4][1][0])
        # Repetition level accessed in list-form doesn't make much sense...
        self.assertIs(f, msg["PID.4.2"])

    def test_extract(self):
        msg = hl7.parse(rep_sample_hl7)

        # Full correct path
        self.assertEqual(msg["PID.3.1.2.2"], "Sub-Component2")
        self.assertEqual(msg[Accessor("PID", 1, 3, 1, 2, 2)], "Sub-Component2")

        # Shorter Paths
        self.assertEqual(msg["PID.1.1"], "Field1")
        self.assertEqual(msg[Accessor("PID", 1, 1, 1)], "Field1")
        self.assertEqual(msg["PID.1"], "Field1")
        self.assertEqual(msg["PID1.1"], "Field1")
        self.assertEqual(msg["PID.3.1.2"], "Sub-Component1")

        # Longer Paths
        self.assertEqual(msg["PID.1.1.1.1"], "Field1")

        # Incorrect path
        self.assertRaisesRegex(
            IndexError,
            "PID.1.1.1.2",
            msg.extract_field,
            *Accessor.parse_key("PID.1.1.1.2")
        )

        # Optional field, not included in message
        self.assertEqual(msg["MSH.20"], "")

        # Optional sub-component, not included in message
        self.assertEqual(msg["PID.3.1.2.3"], "")
        self.assertEqual(msg["PID.3.1.3"], "Component3")
        self.assertEqual(msg["PID.3.1.4"], "")

    def test_assign(self):
        msg = hl7.parse(rep_sample_hl7)

        # Field
        msg["MSH.20"] = "FIELD 20"
        self.assertEqual(msg["MSH.20"], "FIELD 20")

        # Component
        msg["MSH.21.1.1"] = "COMPONENT 21.1.1"
        self.assertEqual(msg["MSH.21.1.1"], "COMPONENT 21.1.1")

        # Sub-Component
        msg["MSH.21.1.2.4"] = "SUBCOMPONENT 21.1.2.4"
        self.assertEqual(msg["MSH.21.1.2.4"], "SUBCOMPONENT 21.1.2.4")

        # Verify round-tripping (i.e. that separators are correct)
        msg2 = hl7.parse(str(msg))
        self.assertEqual(msg2["MSH.20"], "FIELD 20")
        self.assertEqual(msg2["MSH.21.1.1"], "COMPONENT 21.1.1")
        self.assertEqual(msg2["MSH.21.1.2.4"], "SUBCOMPONENT 21.1.2.4")

    def test_unescape(self):
        msg = hl7.parse(rep_sample_hl7)

        # Replace Separators
        self.assertEqual(msg.unescape("\\E\\"), "\\")
        self.assertEqual(msg.unescape("\\F\\"), "|")
        self.assertEqual(msg.unescape("\\S\\"), "^")
        self.assertEqual(msg.unescape("\\T\\"), "&")
        self.assertEqual(msg.unescape("\\R\\"), "~")

        # Replace Highlighting
        self.assertEqual(msg.unescape("\\H\\text\\N\\"), "_text_")

        # Application Overrides
        self.assertEqual(msg.unescape("\\H\\text\\N\\", {"H": "*", "N": "*"}), "*text*")

        # Hex Codes
        self.assertEqual(msg.unescape("\\X20202020\\"), "    ")
        self.assertEqual(msg.unescape("\\Xe1\\\\Xe9\\\\Xed\\\\Xf3\\\\Xfa\\"), "áéíóú")

    def test_escape(self):
        msg = hl7.parse(rep_sample_hl7)

        # Escape Separators
        self.assertEqual(msg.escape("\\"), "\\E\\")
        self.assertEqual(msg.escape("|"), "\\F\\")
        self.assertEqual(msg.escape("^"), "\\S\\")
        self.assertEqual(msg.escape("&"), "\\T\\")
        self.assertEqual(msg.escape("~"), "\\R\\")

        # Escape ASCII characters
        self.assertEqual(msg.escape("asdf"), "asdf")

        # Escape non-ASCII characters
        self.assertEqual(msg.escape("áéíóú"), "\\Xe1\\\\Xe9\\\\Xed\\\\Xf3\\\\Xfa\\")
        self.assertEqual(msg.escape("äsdf"), "\\Xe4\\sdf")

    def test_file(self):
        # Extract message from file
        self.assertTrue(hl7.isfile(sample_file))
        messages = hl7.split_file(sample_file)
        self.assertEqual(len(messages), 1)

        # message can be parsed
        msg = hl7.parse(messages[0])

        # message has expected content
        self.assertEqual(
            [s[0][0] for s in msg], ["MSH", "EVN", "PID", "PD1", "NK1", "PV1"]
        )


class ParsePlanTest(TestCase):
    def test_create_parse_plan(self):
        plan = hl7.parser.create_parse_plan(sample_hl7)

        self.assertEqual(plan.separators, "\r|~^&")
        self.assertEqual(
            plan.containers, [Message, Segment, Field, Repetition, Component]
        )

    def test_parse_plan(self):
        plan = hl7.parser.create_parse_plan(sample_hl7)

        self.assertEqual(plan.separator, "\r")
        con = plan.container([1, 2])
        self.assertIsInstance(con, Message)
        self.assertEqual(con, [1, 2])
        self.assertEqual(con.separator, "\r")

    def test_parse_plan_next(self):
        plan = hl7.parser.create_parse_plan(sample_hl7)

        n1 = plan.next()
        self.assertEqual(n1.separators, "\r|~^&")
        self.assertEqual(n1.separator, "|")
        self.assertEqual(n1.containers, [Segment, Field, Repetition, Component])

        n2 = n1.next()
        self.assertEqual(n2.separators, "\r|~^&")
        self.assertEqual(n2.separator, "~")
        self.assertEqual(n2.containers, [Field, Repetition, Component])

        n3 = n2.next()
        self.assertEqual(n3.separators, "\r|~^&")
        self.assertEqual(n3.separator, "^")
        self.assertEqual(n3.containers, [Repetition, Component])

        n4 = n3.next()
        self.assertEqual(n4.separators, "\r|~^&")
        self.assertEqual(n4.separator, "&")
        self.assertEqual(n4.containers, [Component])

        n5 = n4.next()
        self.assertTrue(n5 is None)
