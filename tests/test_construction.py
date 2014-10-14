# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import six

from .compat import unittest
import hl7
from .samples import rep_sample_hl7


SEP = '|^~\&'
CR_SEP = '\r'


class ConstructionTest(unittest.TestCase):
    def test_create_msg(self):
        # Create a message
        MSH = hl7.Segment(SEP[0], [hl7.Field(SEP[1], ['MSH'])])
        MSA = hl7.Segment(SEP[0], [hl7.Field(SEP[1], ['MSA'])])
        response = hl7.Message(CR_SEP, [MSH, MSA])
        response['MSH.F1.R1'] = SEP[0]
        response['MSH.F2.R1'] = SEP[1:]
        self.assertEqual(six.text_type(response), 'MSH|^~\\&|\rMSA')

    def test_append(self):
        # Append a segment to a message
        MSH = hl7.Segment(SEP[0], [hl7.Field(SEP[1], ['MSH'])])
        response = hl7.Message(CR_SEP, [MSH])
        response['MSH.F1.R1'] = SEP[0]
        response['MSH.F2.R1'] = SEP[1:]
        MSA = hl7.Segment(SEP[0], [hl7.Field(SEP[1], ['MSA'])])
        response.append(MSA)
        self.assertEqual(six.text_type(response), 'MSH|^~\\&|\rMSA')

    def test_append_from_source(self):
        # Copy a segment between messages
        MSH = hl7.Segment(SEP[0], [hl7.Field(SEP[1], ['MSH'])])
        MSA = hl7.Segment(SEP[0], [hl7.Field(SEP[1], ['MSA'])])
        response = hl7.Message(CR_SEP, [MSH, MSA])
        response['MSH.F1.R1'] = SEP[0]
        response['MSH.F2.R1'] = SEP[1:]
        self.assertEqual(six.text_type(response), 'MSH|^~\\&|\rMSA')
        src_msg = hl7.parse(rep_sample_hl7)
        PID = src_msg['PID'][0]
        self.assertEqual(six.text_type(PID), 'PID|Field1|Component1^Component2|Component1^Sub-Component1&Sub-Component2^Component3|Repeat1~Repeat2')
        response.append(PID)
        self.assertEqual(six.text_type(response), 'MSH|^~\\&|\rMSA\rPID|Field1|Component1^Component2|Component1^Sub-Component1&Sub-Component2^Component3|Repeat1~Repeat2')
