# -*- coding: utf-8 -*-
from __future__ import unicode_literals


# Sample message from HL7 Normative Edition
# http://healthinfo.med.dal.ca/hl7intro/CDA_R2_normativewebedition/help/v3guide/v3guide.htm#v3gexamples
sample_hl7 = '\r'.join([
    'MSH|^~\&|GHH LAB|ELAB-3|GHH OE|BLDG4|200202150930||ORU^R01|CNTRL-3456|P|2.4', # noqa
    'PID|||555-44-4444||EVERYWOMAN^EVE^E^^^^L|JONES|196203520|F|||153 FERNWOOD DR.^^STATESVILLE^OH^35292||(206)3345232|(206)752-121||||AC555444444||67-A4335^OH^20030520', # noqa
    'OBR|1|845439^GHH OE|1045813^GHH LAB|1554-5^GLUCOSE|||200202150730||||||||555-55-5555^PRIMARY^PATRICIA P^^^^MD^^LEVEL SEVEN HEALTHCARE, INC.|||||||||F||||||444-44-4444^HIPPOCRATES^HOWARD H^^^^MD', # noqa
    'OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F', # noqa
    'OBX|2|FN|1553-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F\r' # noqa
])

# Example from: http://wiki.medical-objects.com.au/index.php/Hl7v2_parsing
rep_sample_hl7 = '\r'.join([
    'MSH|^~\&|GHH LAB|ELAB-3|GHH OE|BLDG4|200202150930||ORU^R01|CNTRL-3456|P|2.4', # noqa
    'PID|Field1|Component1^Component2|Component1^Sub-Component1&Sub-Component2^Component3|Repeat1~Repeat2', # noqa
    ''
    ])

# Source: http://www.health.vic.gov.au/hdss/vinah/2006-07/appendix-a-sample-messages.pdf
sample_file = '\r'.join([
    'FHS|^~\&||ABCHS||AUSDHSV|20070101123401|||abchs20070101123401.hl7|', # noqa
    'BHS|^~\&||ABCHS||AUSDHSV|20070101123401||||abchs20070101123401-1', # noqa
    'MSH|^~\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778890|P|2.5|||NE|NE|AU|ASCII', # noqa
    'EVN|A04|20060705000000', # noqa
    'PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA', # noqa
    'PD1||2', # noqa
    'NK1|1||1||||||||||||||||||2', # noqa
    'PV1|1|O||||^^^^^1', # noqa
    'BTS|1', # noqa
    'FTS|1', # noqa
    '' # noqa
    ])
