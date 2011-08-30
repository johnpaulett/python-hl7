# -*- coding: utf-8 -*-
from hl7 import Message, Segment, Field

import hl7
import unittest

## Sample message from HL7 Normative Edition
## http://healthinfo.med.dal.ca/hl7intro/CDA_R2_normativewebedition/help/v3guide/v3guide.htm#v3gexamples
sample_hl7 = u'\r'.join([
    'MSH|^~\&|GHH LAB|ELAB-3|GHH OE|BLDG4|200202150930||ORU^R01|CNTRL-3456|P|2.4',
    'PID|||555-44-4444||EVERYWOMAN^EVE^E^^^^L|JONES|196203520|F|||153 FERNWOOD DR.^^STATESVILLE^OH^35292||(206)3345232|(206)752-121||||AC555444444||67-A4335^OH^20030520',
    'OBR|1|845439^GHH OE|1045813^GHH LAB|1554-5^GLUCOSE|||200202150730||||||||555-55-5555^PRIMARY^PATRICIA P^^^^MD^^LEVEL SEVEN HEALTHCARE, INC.|||||||||F||||||444-44-4444^HIPPOCRATES^HOWARD H^^^^MD',
    'OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F',
    'OBX|2|FN|1553-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F\r'
])

class ParseTest(unittest.TestCase):
    def test_parse(self):
        msg = hl7.parse(sample_hl7)
        self.assertEqual(len(msg), 5)
        self.assertTrue(isinstance(msg[0][0][0], unicode))
        self.assertEqual(msg[0][0][0], u'MSH')
        self.assertEqual(msg[3][0][0], u'OBX')
        self.assertEqual(
            msg[3][3],
            [u'1554-5', u'GLUCOSE', u'POST 12H CFST:MCNC:PT:SER/PLAS:QN']
        )

    def test_bytestring_converted_to_unicode(self):
        msg = hl7.parse(str(sample_hl7))
        self.assertEqual(len(msg), 5)
        self.assertTrue(isinstance(msg[0][0][0], unicode))
        self.assertEqual(msg[0][0][0], u'MSH')

    def test_non_ascii_bytestring(self):
        # \x96 - valid cp1252, not valid utf8
        # it is the responsibility of the caller to convert to unicode
        self.assertRaises(UnicodeDecodeError, hl7.parse,
                          'MSH|^~\&|GHH LAB|ELAB\x963')

    def test_parsing_classes(self):
        msg = hl7.parse(sample_hl7)

        self.assertTrue(isinstance(msg, hl7.Message))
        self.assertTrue(isinstance(msg[3], hl7.Segment))
        self.assertTrue(isinstance(msg[3][0], hl7.Field))
        self.assertTrue(isinstance(msg[3][0][0], unicode))

    def test_nonstandard_separators(self):
        nonstd = 'MSH$%~\&$GHH LAB\rPID$$$555-44-4444$$EVERYWOMAN%EVE%E%%%L'
        msg = hl7.parse(nonstd)

        self.assertEqual(unicode(msg), nonstd)
        self.assertEqual(len(msg), 2)
        self.assertEqual(msg[1][5], ['EVERYWOMAN', 'EVE', 'E', '', '', 'L'])


class IsHL7Test(unittest.TestCase):
    def test_ishl7(self):
        self.assertTrue(hl7.ishl7(sample_hl7))

    def test_ishl7_empty(self):
        self.assertFalse(hl7.ishl7(''))

    def test_ishl7_None(self):
        self.assertFalse(hl7.ishl7(None))

    def test_ishl7_wrongsegment(self):
        message = 'OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F\r'
        self.assertFalse(hl7.ishl7(message))

class ContainerTest(unittest.TestCase):
    def test_unicode(self):
        msg = hl7.parse(sample_hl7)
        self.assertEqual(unicode(msg), sample_hl7.strip())
        self.assertEqual(
            unicode(msg[3][3]),
            '1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN'
        )

    def test_container_unicode(self):
        c = hl7.Container('|')
        c.extend(['1', 'b', 'data'])
        self.assertEqual(unicode(c), '1|b|data')

class MessageTest(unittest.TestCase):
    def test_segments(self):
        msg = hl7.parse(sample_hl7)
        s = msg.segments('OBX')
        self.assertEqual(len(s), 2)
        self.assertEqual(s[0][0:3], [['OBX'], ['1'], ['SN']])
        self.assertEqual(s[1][0:3], [['OBX'], ['2'], ['FN']])

    def test_segments_does_not_exist(self):
        msg = hl7.parse(sample_hl7)
        self.assertRaises(KeyError, msg.segments, 'BAD')

    def test_segment(self):
        msg = hl7.parse(sample_hl7)
        s = msg.segment('OBX')
        self.assertEqual(s[0:3], [['OBX'], ['1'], ['SN']])

    def test_segment_does_not_exist(self):
        msg = hl7.parse(sample_hl7)
        self.assertRaises(KeyError, msg.segment, 'BAD')

    def test_segments_dict_key(self):
        msg = hl7.parse(sample_hl7)
        s = msg['OBX']
        self.assertEqual(len(s), 2)
        self.assertEqual(s[0][0:3], [['OBX'], ['1'], ['SN']])
        self.assertEqual(s[1][0:3], [['OBX'], ['2'], ['FN']])

class ParsePlanTest(unittest.TestCase):
    def test_create_parse_plan(self):
        plan = hl7.create_parse_plan(sample_hl7)

        self.assertEqual(plan.separators, ['\r', '|', '^'])
        self.assertEqual(plan.containers, [Message, Segment, Field])

    def test_parse_plan(self):
        plan = hl7.create_parse_plan(sample_hl7)

        self.assertEqual(plan.separator, '\r')
        con = plan.container([1, 2])
        self.assertTrue(isinstance(con, Message))
        self.assertEqual(con, [1, 2])
        self.assertEqual(con.separator, '\r')

    def test_parse_plan_next(self):
        plan = hl7.create_parse_plan(sample_hl7)

        n1 = plan.next()
        self.assertEqual(n1.separators, ['|', '^'])
        self.assertEqual(n1.containers, [Segment, Field])

        n2 = n1.next()
        self.assertEqual(n2.separators, ['^'])
        self.assertEqual(n2.containers, [Field])

        n3 = n2.next()
        self.assertTrue(n3 is None)

if __name__ == '__main__':
    unittest.main()
