# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 John Paulett (john -at- 7oars.com)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

import hl7
from hl7 import *

## Sample message from HL7 Normative Edition
## http://healthinfo.med.dal.ca/hl7intro/CDA_R2_normativewebedition/help/v3guide/v3guide.htm#v3gexamples
sample_hl7 = '\r'.join(['MSH|^~\&|GHH LAB|ELAB-3|GHH OE|BLDG4|200202150930||ORU^R01|CNTRL-3456|P|2.4',
                        'PID|||555-44-4444||EVERYWOMAN^EVE^E^^^^L|JONES|196203520|F|||153 FERNWOOD DR.^^STATESVILLE^OH^35292||(206)3345232|(206)752-121||||AC555444444||67-A4335^OH^20030520',
                        'OBR|1|845439^GHH OE|1045813^GHH LAB|1554-5^GLUCOSE|||200202150730||||||||555-55-5555^PRIMARY^PATRICIA P^^^^MD^^LEVEL SEVEN HEALTHCARE, INC.|||||||||F||||||444-44-4444^HIPPOCRATES^HOWARD H^^^^MD',
                        'OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F',
                        'OBX|2|FN|1553-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F\r'])

def test_parse():
    msg = hl7.parse(sample_hl7)
    assert len(msg) == 5
    assert msg[0][0][0] == 'MSH'
    assert msg[3][0][0] == 'OBX'
    assert msg[3][3] == ['1554-5', 'GLUCOSE', 'POST 12H CFST:MCNC:PT:SER/PLAS:QN']
    
def test_parse_str():
    msg = hl7.parse(sample_hl7)
    assert str(msg) == sample_hl7.strip()
    assert str(msg[3][3]) == '1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN'
         
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
    msg = hl7.parse(sample_hl7)
    
    assert isinstance(msg, hl7.Message)
    assert isinstance(msg[3], hl7.Segment)
    assert isinstance(msg[3][0], hl7.Field)
    assert isinstance(msg[3][0][0], str)

def test_create_parse_plan():
    plan = hl7.create_parse_plan(sample_hl7)

    assert plan.separators == ['\r', '|', '^']
    assert plan.containers == [Message, Segment, Field]

def test_parse_plan():
    plan = hl7.create_parse_plan(sample_hl7)

    assert plan.separator == '\r'
    con = plan.container([1, 2])
    assert isinstance(con, Message)
    assert con == [1, 2]
    assert con.separator == '\r'

def test_parse_plan_next():
    plan = hl7.create_parse_plan(sample_hl7)

    n1 = plan.next()
    assert n1.separators == ['|', '^']
    assert n1.containers == [Segment, Field]
    
    n2 = n1.next()
    assert n2.separators == ['^']
    assert n2.containers == [Field]

    n3 = n2.next()
    assert n3 is None
    
def test_nonstandard_separators():
    nonstd = 'MSH$%~\&$GHH LAB\rPID$$$555-44-4444$$EVERYWOMAN%EVE%E%%%L'
    msg = hl7.parse(nonstd)

    assert str(msg) == nonstd
    assert len(msg) == 2
    assert msg[1][5] == ['EVERYWOMAN', 'EVE', 'E', '', '', 'L']

        
if __name__ == '__main__':
    import doctest
    import nose
    #doctest.testmod(hl7)
    nose.main()
