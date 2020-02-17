from unittest import TestCase
from unittest.mock import patch

from hl7.version import get_version


class GetVersionTest(TestCase):
    @patch("hl7.version.VERSION", new=(0, 4, 1))
    def test_no_modifier(self):
        self.assertEqual("0.4.1", get_version())

    @patch("hl7.version.VERSION", new=(0, 4, 1, ""))
    def test_empty_modifier(self):
        self.assertEqual("0.4.1", get_version())

    @patch("hl7.version.VERSION", new=(0, 4, 1, None))
    def test_none_modifier(self):
        self.assertEqual("0.4.1", get_version())

    @patch("hl7.version.VERSION", new=(0, 4, 1, "final"))
    def test_final(self):
        self.assertEqual("0.4.1", get_version())

    @patch("hl7.version.VERSION", new=(0, 4, 1, "rc"))
    def test_rc(self):
        self.assertEqual("0.4.1rc", get_version())

    @patch("hl7.version.VERSION", new=(0, 4, 1, "rc4"))
    def test_rc_num(self):
        self.assertEqual("0.4.1rc4", get_version())

    @patch("hl7.version.VERSION", new=(0, 4, 1, "b"))
    def test_beta(self):
        self.assertEqual("0.4.1b", get_version())

    @patch("hl7.version.VERSION", new=(0, 4, 1, "a"))
    def test_alpha(self):
        self.assertEqual("0.4.1a", get_version())

    @patch("hl7.version.VERSION", new=(0, 4, 1, "dev"))
    def test_dev(self):
        self.assertEqual("0.4.1.dev", get_version())
