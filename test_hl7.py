# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 John Paulett (john -at- 7oars.com)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

import hl7

## Sample message from HL7 Normative Edition
## http://healthinfo.med.dal.ca/hl7intro/CDA_R2_normativewebedition/help/v3guide/v3guide.htm#v3gexamples
sample_hl7 = '\r'.join(['MSH|^~\&|GHH LAB|ELAB-3|GHH OE|BLDG4|200202150930||ORU^R01|CNTRL-3456|P|2.4',
                        'PID|||555-44-4444||EVERYWOMAN^EVE^E^^^^L|JONES|196203520|F|||153 FERNWOOD DR.^^STATESVILLE^OH^35292||(206)3345232|(206)752-121||||AC555444444||67-A4335^OH^20030520',
                        'OBR|1|845439^GHH OE|1045813^GHH LAB|1554-5^GLUCOSE|||200202150730||||||||555-55-5555^PRIMARY^PATRICIA P^^^^MD^^LEVEL SEVEN HEALTHCARE, INC.|||||||||F||||||444-44-4444^HIPPOCRATES^HOWARD H^^^^MD',
                        'OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F',
                        'OBX|2|FN|1553-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F\r'])

def test_parse():
    h = hl7.parse(sample_hl7)
    assert 5 == len(h)
    assert h[0][0][0] == 'MSH'
    assert h[3][0][0] == 'OBX'
    assert h[3][3] == ['1554-5', 'GLUCOSE', 'POST 12H CFST:MCNC:PT:SER/PLAS:QN']
    
def test_parse_str():
    h = hl7.parse(sample_hl7)
    assert str(h) == sample_hl7.strip()
    assert str(h[3][3]) == '1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN'
         
def test_ishl7():
    assert hl7.ishl7(sample_hl7)

def test_ishl7_empty():
    assert not hl7.ishl7('')

def test_ishl7_None():
    assert not hl7.ishl7(None)

def test_ishl7_wrongsegment():
    message = 'OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F\r'
    assert not hl7.ishl7(message)

def test_segments():
    s = hl7.segments('OBX', hl7.parse(sample_hl7))
    assert len(s) == 2 
    assert s[0][0:3] == [['OBX'], ['1'], ['SN']]
    assert s[1][0:3] == [['OBX'], ['2'], ['FN']]

def test_segment():
    s = hl7.segment('OBX', hl7.parse(sample_hl7))
    assert s[0:3] == [['OBX'], ['1'], ['SN']]

#####################
def test_container_str():
    c = hl7.Container('|')
    c.extend(['1', 'b', 'data'])
    assert str(c) == '1|b|data'

def test_parsing_classes():
    h = hl7.parse(sample_hl7)
    
    assert isinstance(h, hl7.Message)
    assert isinstance(h[3], hl7.Segment)
    assert isinstance(h[3][0], hl7.Field)
    assert isinstance(h[3][0][0], str)
   

if __name__ == '__main__':
    import doctest
    import nose
    #doctest.testmod(hl7)
    nose.main()
