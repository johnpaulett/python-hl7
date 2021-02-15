# -*- coding: utf-8 -*-

# Sample message from HL7 Normative Edition
# http://healthinfo.med.dal.ca/hl7intro/CDA_R2_normativewebedition/help/v3guide/v3guide.htm#v3gexamples
sample_hl7 = "\r".join(
    [
        "MSH|^~\\&|GHH LAB|ELAB-3|GHH OE|BLDG4|200202150930||ORU^R01|CNTRL-3456|P|2.4",
        "PID|||555-44-4444||EVERYWOMAN^EVE^E^^^^L|JONES|196203520|F|||153 FERNWOOD DR.^^STATESVILLE^OH^35292||(206)3345232|(206)752-121||||AC555444444||67-A4335^OH^20030520",
        "OBR|1|845439^GHH OE|1045813^GHH LAB|1554-5^GLUCOSE|||200202150730||||||||555-55-5555^PRIMARY^PATRICIA P^^^^MD^^LEVEL SEVEN HEALTHCARE, INC.|||||||||F||||||444-44-4444^HIPPOCRATES^HOWARD H^^^^MD",
        "OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F",
        "OBX|2|FN|1553-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F\r",
    ]
)

# Example from: http://wiki.medical-objects.com.au/index.php/Hl7v2_parsing
rep_sample_hl7 = "\r".join(
    [
        "MSH|^~\\&|GHH LAB|ELAB-3|GHH OE|BLDG4|200202150930||ORU^R01|CNTRL-3456|P|2.4",
        "PID|Field1|Component1^Component2|Component1^Sub-Component1&Sub-Component2^Component3|Repeat1~Repeat2",
        "",
    ]
)

# Source: http://www.health.vic.gov.au/hdss/vinah/2006-07/appendix-a-sample-messages.pdf
sample_batch = "\r".join(
    [
        "BHS|^~\\&||ABCHS||AUSDHSV|20070101123401||||abchs20070101123401-1",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778890|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "BTS|1",
        "",
    ]
)

sample_batch1 = "\r".join(
    [
        "BHS|^~\\&||ABCHS||AUSDHSV|20070101123401||||abchs20070101123401-1",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778890|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778891|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "BTS|2",
        "",
    ]
)

sample_batch2 = "\r".join(
    [
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778890|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778891|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "",
    ]
)

sample_batch3 = "\r".join(
    [
        "BHS|^~\\&||ABCHS||AUSDHSV|20070101123401||||abchs20070101123401-1",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778890|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "",
    ]
)


sample_batch4 = "\r".join(
    [
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778890|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "BTS|1",
        "",
    ]
)

sample_bad_batch = "\r".join(
    [
        "BHS|^~\\&||ABCHS||AUSDHSV|20070101123401||||abchs20070101123401-1",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "BTS|1",
        "",
    ]
)

sample_bad_batch1 = "\r".join(
    [
        "BHS|^~\\&||ABCHS||AUSDHSV|20070101123401||||abchs20070101123401-1",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778890|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "BHS|^~\\&||ABCHS||AUSDHSV|20070101123402||||abchs20070101123401-1",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "BTS|1",
        "",
    ]
)

# Source: http://www.health.vic.gov.au/hdss/vinah/2006-07/appendix-a-sample-messages.pdf
sample_file = "\r".join(
    [
        "FHS|^~\\&||ABCHS||AUSDHSV|20070101123401|||abchs20070101123401.hl7|",
        "BHS|^~\\&||ABCHS||AUSDHSV|20070101123401||||abchs20070101123401-1",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778890|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "BTS|1",
        "FTS|1",
        "",
    ]
)

sample_file1 = "\r".join(
    [
        "FHS|^~\\&||ABCHS||AUSDHSV|20070101123401|||abchs20070101123401.hl7|",
        "BHS|^~\\&||ABCHS||AUSDHSV|20070101123401||||abchs20070101123401-1",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778890|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778891|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "BTS|2",
        "BHS|^~\\&||ABCHS||AUSDHSV|20070101123401||||abchs20070101123401-2",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778890|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "BTS|1",
        "FTS|2",
        "",
    ]
)

sample_file2 = "\r".join(
    [
        "FHS|^~\\&||ABCHS||AUSDHSV|20070101123401|||abchs20070101123401.hl7|",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778890|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778891|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "FTS|1",
        "",
    ]
)

sample_file3 = "\r".join(
    [
        "FHS|^~\\&||ABCHS||AUSDHSV|20070101123401|||abchs20070101123401.hl7|",
        "BHS|^~\\&||ABCHS||AUSDHSV|20070101123401||||abchs20070101123401-1",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778890|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "BTS|1",
        "",
    ]
)

sample_file4 = "\r".join(
    [
        "BHS|^~\\&||ABCHS||AUSDHSV|20070101123401||||abchs20070101123401-1",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778890|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "BTS|1",
        "FTS|1",
        "",
    ]
)

sample_file5 = "\r".join(
    [
        "FHS|^~\\&||ABCHS||AUSDHSV|20070101123401|||abchs20070101123401.hl7|",
        "BHS|^~\\&||ABCHS||AUSDHSV|20070101123401||||abchs20070101123401-1",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778890|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "FTS|1",
        "",
    ]
)

sample_file6 = "\r".join(
    [
        "FHS|^~\\&||ABCHS||AUSDHSV|20070101123401|||abchs20070101123401.hl7|",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778890|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "BTS|1",
        "FTS|1",
        "",
    ]
)

sample_bad_file = "\r".join(
    [
        "FHS|^~\\&||ABCHS||AUSDHSV|20070101123401|||abchs20070101123401.hl7|",
        "BHS|^~\\&||ABCHS||AUSDHSV|20070101123401||||abchs20070101123401-1",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "BTS|1",
        "FTS|1",
        "",
    ]
)

sample_bad_file1 = "\r".join(
    [
        "FHS|^~\\&||ABCHS||AUSDHSV|20070101123401|||abchs20070101123401.hl7|",
        "BHS|^~\\&||ABCHS||AUSDHSV|20070101123401||||abchs20070101123401-1",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778890|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "BHS|^~\\&||ABCHS||AUSDHSV|20070101123402||||abchs20070101123401-1",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "BTS|1",
        "FTS|1",
        "",
    ]
)

sample_bad_file2 = "\r".join(
    [
        "FHS|^~\\&||ABCHS||AUSDHSV|20070101123401|||abchs20070101123401.hl7|",
        "BHS|^~\\&||ABCHS||AUSDHSV|20070101123401||||abchs20070101123401-1",
        "MSH|^~\\&||ABCHS||AUSDHSV|20070101112951||ADT^A04^ADT_A01|12334456778890|P|2.5|||NE|NE|AU|ASCII",
        "EVN|A04|20060705000000",
        "FHS|^~\\&||ABCHS||AUSDHSV|20070101123402|||abchs20070101123401.hl7|",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "BTS|1",
        "FTS|1",
        "",
    ]
)

sample_bad_file3 = "\r".join(
    [
        "FHS|^~\\&||ABCHS||AUSDHSV|20070101123401|||abchs20070101123401.hl7|",
        "EVN|A04|20060705000000",
        "PID|1||0000112234^^^100^A||XXXXXXXXXX^^^^^^S||10131113|1||4|^^RICHMOND^^3121||||1201||||||||1100|||||||||AAA",
        "PD1||2",
        "NK1|1||1||||||||||||||||||2",
        "PV1|1|O||||^^^^^1",
        "FTS|1",
        "",
    ]
)
