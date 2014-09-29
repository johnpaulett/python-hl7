# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import hl7
from .compat import unittest
from .samples import sample_hl7, sample_file


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

    def test_isfile(self):
        self.assertFalse(hl7.ishl7(sample_file))
        self.assertTrue(hl7.isfile(sample_file))
