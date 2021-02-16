# -*- coding: utf-8 -*-
from unittest import TestCase

import hl7

from .samples import rep_sample_hl7

SEP = r"|^~\&"
CR_SEP = "\r"


class ConstructionTest(TestCase):
    def test_create_msg(self):
        # Create a message
        MSH = hl7.Segment(SEP[0], [hl7.Field(SEP[2], ["MSH"])])
        MSA = hl7.Segment(SEP[0], [hl7.Field(SEP[2], ["MSA"])])
        response = hl7.Message(CR_SEP, [MSH, MSA])
        response["MSH.F1.R1"] = SEP[0]
        response["MSH.F2.R1"] = SEP[1:]
        self.assertEqual(str(response), "MSH|^~\\&|\rMSA\r")

    def test_append(self):
        # Append a segment to a message
        MSH = hl7.Segment(SEP[0], [hl7.Field(SEP[2], ["MSH"])])
        response = hl7.Message(CR_SEP, [MSH])
        response["MSH.F1.R1"] = SEP[0]
        response["MSH.F2.R1"] = SEP[1:]
        MSA = hl7.Segment(SEP[0], [hl7.Field(SEP[2], ["MSA"])])
        response.append(MSA)
        self.assertEqual(str(response), "MSH|^~\\&|\rMSA\r")

    def test_append_from_source(self):
        # Copy a segment between messages
        MSH = hl7.Segment(SEP[0], [hl7.Field(SEP[2], ["MSH"])])
        MSA = hl7.Segment(SEP[0], [hl7.Field(SEP[2], ["MSA"])])
        response = hl7.Message(CR_SEP, [MSH, MSA])
        response["MSH.F1.R1"] = SEP[0]
        response["MSH.F2.R1"] = SEP[1:]
        self.assertEqual(str(response), "MSH|^~\\&|\rMSA\r")
        src_msg = hl7.parse(rep_sample_hl7)
        PID = src_msg["PID"][0]
        self.assertEqual(
            str(PID),
            "PID|Field1|Component1^Component2|Component1^Sub-Component1&Sub-Component2^Component3|Repeat1~Repeat2",
        )
        response.append(PID)
        self.assertEqual(
            str(response),
            "MSH|^~\\&|\rMSA\rPID|Field1|Component1^Component2|Component1^Sub-Component1&Sub-Component2^Component3|Repeat1~Repeat2\r",
        )
