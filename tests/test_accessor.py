# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from hl7 import Accessor
from .compat import unittest


class AccessorTest(unittest.TestCase):
    def test_key(self):
        self.assertEqual("FOO", Accessor("FOO").key)
        self.assertEqual("FOO2", Accessor("FOO", 2).key)
        self.assertEqual("FOO2.3", Accessor("FOO", 2, 3).key)
        self.assertEqual("FOO2.3.1.4.6", Accessor("FOO", 2, 3, 1, 4, 6).key)

    def test_parse(self):
        self.assertEqual(Accessor("FOO"), Accessor.parse_key("FOO"))
        self.assertEqual(Accessor("FOO", 2, 3, 1, 4, 6), Accessor.parse_key("FOO2.3.1.4.6"))

    def test_equality(self):
        self.assertEqual(Accessor("FOO", 1, 3, 4), Accessor("FOO", 1, 3, 4))
        self.assertNotEqual(Accessor("FOO", 1), Accessor("FOO", 2))
