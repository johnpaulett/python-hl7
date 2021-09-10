# -*- coding: utf-8 -*-
from unittest import TestCase

import hl7

from .samples import (
    sample_batch,
    sample_batch1,
    sample_batch2,
    sample_file,
    sample_file1,
    sample_file2,
    sample_hl7,
    sample_msh,
)


class IsHL7Test(TestCase):
    def test_ishl7(self):
        self.assertTrue(hl7.ishl7(sample_hl7))
        self.assertFalse(hl7.ishl7(sample_batch))
        self.assertFalse(hl7.ishl7(sample_batch1))
        self.assertFalse(hl7.ishl7(sample_batch2))
        self.assertFalse(hl7.ishl7(sample_file))
        self.assertFalse(hl7.ishl7(sample_file1))
        self.assertFalse(hl7.ishl7(sample_file2))
        self.assertTrue(hl7.ishl7(sample_msh))

    def test_ishl7_empty(self):
        self.assertFalse(hl7.ishl7(""))

    def test_ishl7_None(self):
        self.assertFalse(hl7.ishl7(None))

    def test_ishl7_wrongsegment(self):
        message = "OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F\r"
        self.assertFalse(hl7.ishl7(message))

    def test_isbatch(self):
        self.assertFalse(hl7.ishl7(sample_batch))
        self.assertFalse(hl7.ishl7(sample_batch1))
        self.assertFalse(hl7.ishl7(sample_batch2))
        self.assertTrue(hl7.isbatch(sample_batch))
        self.assertTrue(hl7.isbatch(sample_batch1))
        self.assertTrue(hl7.isbatch(sample_batch2))

    def test_isfile(self):
        self.assertFalse(hl7.ishl7(sample_file))
        self.assertFalse(hl7.ishl7(sample_file1))
        self.assertFalse(hl7.ishl7(sample_file2))
        self.assertFalse(hl7.isbatch(sample_file))
        self.assertFalse(hl7.isbatch(sample_file1))
        self.assertFalse(hl7.isbatch(sample_file2))
        self.assertTrue(hl7.isfile(sample_file))
        self.assertTrue(hl7.isfile(sample_file1))
        self.assertTrue(hl7.isfile(sample_file2))
        self.assertTrue(hl7.isfile(sample_batch))
        self.assertTrue(hl7.isfile(sample_batch1))
        self.assertTrue(hl7.isfile(sample_batch2))
