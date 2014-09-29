# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import six
import hl7
from hl7 import Accessor, Message, Segment, Field, Repetition, Component
from .compat import unittest
from .samples import sample_hl7, rep_sample_hl7, sample_file


class ParseTest(unittest.TestCase):
    def test_parse(self):
        msg = hl7.parse(sample_hl7)
        self.assertEqual(len(msg), 5)
        self.assertIsInstance(msg[0][0][0], six.text_type)
        self.assertEqual(msg[0][0][0], 'MSH')
        self.assertEqual(msg[3][0][0], 'OBX')
        self.assertEqual(
            msg[3][3],
            [[['1554-5'], ['GLUCOSE'], ['POST 12H CFST:MCNC:PT:SER/PLAS:QN']]]
        )
        # Make sure MSH-1 and MSH-2 are valid
        self.assertEqual(msg[0][1][0], '|')
        self.assertIsInstance(msg[0][1], hl7.Field)
        self.assertEqual(msg[0][2][0], '^~\&')
        self.assertIsInstance(msg[0][2], hl7.Field)
        # MSH-9 is the message type
        self.assertEqual(msg[0][9], [[['ORU'], ['R01']]])
        # Do it twice to make sure text coercion is idempotent
        self.assertEqual(six.text_type(msg), sample_hl7.strip())
        self.assertEqual(six.text_type(msg), sample_hl7.strip())

    def test_bytestring_converted_to_unicode(self):
        msg = hl7.parse(six.text_type(sample_hl7))
        self.assertEqual(len(msg), 5)
        self.assertIsInstance(msg[0][0][0], six.text_type)
        self.assertEqual(msg[0][0][0], 'MSH')

    def test_non_ascii_bytestring(self):
        # \x96 - valid cp1252, not valid utf8
        # it is the responsibility of the caller to convert to unicode
        msg = hl7.parse(b'MSH|^~\&|GHH LAB|ELAB\x963', encoding='cp1252')
        self.assertEqual(msg[0][4][0], 'ELAB\u20133')

    def test_non_ascii_bytestring_no_encoding(self):
        # \x96 - valid cp1252, not valid utf8
        # it is the responsibility of the caller to convert to unicode
        self.assertRaises(UnicodeDecodeError, hl7.parse,
                          b'MSH|^~\&|GHH LAB|ELAB\x963')

    def test_parsing_classes(self):
        msg = hl7.parse(sample_hl7)

        self.assertIsInstance(msg, hl7.Message)
        self.assertIsInstance(msg[3], hl7.Segment)
        self.assertIsInstance(msg[3][0], hl7.Field)
        self.assertIsInstance(msg[3][0][0], six.text_type)

    def test_nonstandard_separators(self):
        nonstd = 'MSH$%~\&$GHH LAB\rPID$$$555-44-4444$$EVERYWOMAN%EVE%E%%%L'
        msg = hl7.parse(nonstd)

        self.assertEqual(six.text_type(msg), nonstd)
        self.assertEqual(len(msg), 2)
        self.assertEqual(msg[1][5], [[['EVERYWOMAN'], ['EVE'], ['E'], [''], [''], ['L']]])

    def test_repetition(self):
        msg = hl7.parse(rep_sample_hl7)
        self.assertEqual(msg[1][4], [['Repeat1'], ['Repeat2']])
        self.assertIsInstance(msg[1][4], Field)
        self.assertIsInstance(msg[1][4][0], Repetition)
        self.assertIsInstance(msg[1][4][1], Repetition)
        self.assertEqual(six.text_type(msg[1][4][0][0]), 'Repeat1')
        self.assertIsInstance(msg[1][4][0][0], six.text_type)
        self.assertEqual(six.text_type(msg[1][4][1][0]), 'Repeat2')
        self.assertIsInstance(msg[1][4][1][0], six.text_type)

    def test_empty_initial_repetition(self):
        # Switch to look like "|~Repeat2|
        msg = hl7.parse(rep_sample_hl7.replace('Repeat1', ''))
        self.assertEqual(msg[1][4], [[''], ['Repeat2']])

    def test_subcomponent(self):
        msg = hl7.parse(rep_sample_hl7)
        self.assertEqual(
            msg[1][3],
            [[['Component1'], ['Sub-Component1', 'Sub-Component2'], ['Component3']]]
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
        self.assertEqual(msg['PID.3.1.2.2'], 'Sub-Component2')
        self.assertEqual(msg[Accessor('PID', 1, 3, 1, 2, 2)], 'Sub-Component2')

        # Shorter Paths
        self.assertEqual(msg['PID.1.1'], 'Field1')
        self.assertEqual(msg[Accessor('PID', 1, 1, 1)], 'Field1')
        self.assertEqual(msg['PID.1'], 'Field1')
        self.assertEqual(msg['PID1.1'], 'Field1')
        self.assertEqual(msg['PID.3.1.2'], 'Sub-Component1')

        # Longer Paths
        self.assertEqual(msg['PID.1.1.1.1'], 'Field1')

        # Incorrect path
        self.assertRaisesRegexp(IndexError, 'PID.1.1.1.2', msg.extract_field, *Accessor.parse_key('PID.1.1.1.2'))

        # Optional field, not included in message
        self.assertEqual(msg['MSH.20'], '')

        # Optional sub-component, not included in message
        self.assertEqual(msg['PID.3.1.2.3'], '')
        self.assertEqual(msg['PID.3.1.3'], 'Component3')
        self.assertEqual(msg['PID.3.1.4'], '')

    def test_assign(self):
        msg = hl7.parse(rep_sample_hl7)

        # Field
        msg['MSH.20'] = 'FIELD 20'
        self.assertEqual(msg['MSH.20'], 'FIELD 20')

        # Component
        msg['MSH.21.1.1'] = 'COMPONENT 21.1.1'
        self.assertEqual(msg['MSH.21.1.1'], 'COMPONENT 21.1.1')

        # Sub-Component
        msg['MSH.21.1.2.4'] = 'SUBCOMPONENT 21.1.2.4'
        self.assertEqual(msg['MSH.21.1.2.4'], 'SUBCOMPONENT 21.1.2.4')

        # Verify round-tripping (i.e. that separators are correct)
        msg2 = hl7.parse(six.text_type(msg))
        self.assertEqual(msg2['MSH.20'], 'FIELD 20')
        self.assertEqual(msg2['MSH.21.1.1'], 'COMPONENT 21.1.1')
        self.assertEqual(msg2['MSH.21.1.2.4'], 'SUBCOMPONENT 21.1.2.4')

    def test_unescape(self):
        msg = hl7.parse(rep_sample_hl7)

        # Replace Separators
        self.assertEqual(msg.unescape('\\E\\'), '\\')
        self.assertEqual(msg.unescape('\\F\\'), '|')
        self.assertEqual(msg.unescape('\\S\\'), '^')
        self.assertEqual(msg.unescape('\\T\\'), '&')
        self.assertEqual(msg.unescape('\\R\\'), '~')

        # Replace Highlighting
        self.assertEqual(msg.unescape('\\H\\text\\N\\'), '_text_')

        # Application Overrides
        self.assertEqual(msg.unescape('\\H\\text\\N\\', {'H': '*', 'N': '*'}), '*text*')

        # Hex Codes
        self.assertEqual(msg.unescape('\\X20202020\\'), '    ')

    def test_escape(self):
        msg = hl7.parse(rep_sample_hl7)

        self.assertEqual(msg.escape('\\'), '\\E\\')
        self.assertEqual(msg.escape('|'), '\\F\\')
        self.assertEqual(msg.escape('^'), '\\S\\')
        self.assertEqual(msg.escape('&'), '\\T\\')
        self.assertEqual(msg.escape('~'), '\\R\\')

        self.assertEqual(msg.escape('áéíóú'), '\\Xe1\\\\Xe9\\\\Xed\\\\Xf3\\\\Xfa\\')

    def test_file(self):
        # Extract message from file
        self.assertTrue(hl7.isfile(sample_file))
        messages = hl7.split_file(sample_file)
        self.assertEqual(len(messages), 1)

        # message can be parsed
        msg = hl7.parse(messages[0])

        # message has expected content
        self.assertEqual([s[0][0] for s in msg], ['MSH', 'EVN', 'PID', 'PD1', 'NK1', 'PV1'])


class ParsePlanTest(unittest.TestCase):
    def test_create_parse_plan(self):
        plan = hl7.parser.create_parse_plan(sample_hl7)

        self.assertEqual(plan.separators, ['\r', '|', '~', '^', '&'])
        self.assertEqual(plan.containers, [Message, Segment, Field, Repetition, Component])

    def test_parse_plan(self):
        plan = hl7.parser.create_parse_plan(sample_hl7)

        self.assertEqual(plan.separator, '\r')
        con = plan.container([1, 2])
        self.assertIsInstance(con, Message)
        self.assertEqual(con, [1, 2])
        self.assertEqual(con.separator, '\r')

    def test_parse_plan_next(self):
        plan = hl7.parser.create_parse_plan(sample_hl7)

        n1 = plan.next()
        self.assertEqual(n1.separators, ['|', '~', '^', '&'])
        self.assertEqual(n1.containers, [Segment, Field, Repetition, Component])

        n2 = n1.next()
        self.assertEqual(n2.separators, ['~', '^', '&'])
        self.assertEqual(n2.containers, [Field, Repetition, Component])

        n3 = n2.next()
        self.assertEqual(n3.separators, ['^', '&'])
        self.assertEqual(n3.containers, [Repetition, Component])

        n4 = n3.next()
        self.assertEqual(n4.separators, ['&'])
        self.assertEqual(n4.containers, [Component])

        n5 = n4.next()
        self.assertTrue(n5 is None)
