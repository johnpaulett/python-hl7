# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 John Paulett (john -at- 7oars.com)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

import unittest
import doctest
import hl7

## Sample message from HL7 Normative Edition
## http://healthinfo.med.dal.ca/hl7intro/CDA_R2_normativewebedition/help/v3guide/v3guide.htm#v3gexamples
sample_hl7 = '\r'.join(['MSH|^~\&|GHH LAB|ELAB-3|GHH OE|BLDG4|200202150930||ORU^R01|CNTRL-3456|P|2.4',
                        'PID|||555-44-4444||EVERYWOMAN^EVE^E^^^^L|JONES|196203520|F|||153 FERNWOOD DR.^^STATESVILLE^OH^35292||(206)3345232|(206)752-121||||AC555444444||67-A4335^OH^20030520',
                        'OBR|1|845439^GHH OE|1045813^GHH LAB|1554-5^GLUCOSE|||200202150730||||||||555-55-5555^PRIMARY^PATRICIA P^^^^MD^^LEVEL SEVEN HEALTHCARE, INC.|||||||||F||||||444-44-4444^HIPPOCRATES^HOWARD H^^^^MD',
                        'OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F',
                        'OBX|2|FN|1553-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F\r'])

class ParsingTestCase(unittest.TestCase):
    def setUp(self):
        self.message = sample_hl7

    def test_parse(self):
        h = hl7.parse(self.message)
        self.assertEqual('MSH', h[0][0][0])
        self.assertEqual('OBX', h[3][0][0])
        self.assertEqual(['1554-5', 'GLUCOSE', 'POST 12H CFST:MCNC:PT:SER/PLAS:QN'], h[3][3])
     
class UtilityTestCase(unittest.TestCase):
    def setUp(self):
        self.message = hl7.parse(sample_hl7)

    def test_ishl7(self):
        self.assertTrue(hl7.ishl7(sample_hl7))

    def test_ishl7_empty(self):
        self.assertFalse(hl7.ishl7(''))

    def test_ishl7_None(self):
        self.assertFalse(hl7.ishl7(None))

    def test_ishl7_wrongsegment(self):
        message = 'OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F\r'
        self.assertFalse(hl7.ishl7(message))

    def test_segments(self):
        s = hl7.segments('OBX', self.message)
        self.assertEqual(2, len(s))
        self.assertEqual([['OBX'], ['1'], ['SN']], s[0][0:3])
        self.assertEqual([['OBX'], ['2'], ['FN']], s[1][0:3])

    def test_segment(self):
        s = hl7.segment('OBX', self.message)
        self.assertEqual([['OBX'], ['1'], ['SN']], s[0:3])


def suite():
    suite = unittest.TestSuite()  
    suite.addTest(unittest.makeSuite(ParsingTestCase))
    suite.addTest(unittest.makeSuite(UtilityTestCase))
    suite.addTest(doctest.DocTestSuite(hl7))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
