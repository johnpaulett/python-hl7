import os
import socket
from optparse import Values
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase
from unittest.mock import Mock, patch

import hl7
from hl7 import __version__ as hl7_version
from hl7.client import CR, EB, SB, MLLPClient, MLLPException, mllp_send


class MLLPClientTest(TestCase):
    def setUp(self):
        # use a mock version of socket
        self.socket_patch = patch("hl7.client.socket.socket")
        self.mock_socket = self.socket_patch.start()

        self.client = MLLPClient("localhost", 6666)

    def tearDown(self):
        # unpatch socket
        self.socket_patch.stop()

    def test_connect(self):
        self.mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        self.client.socket.connect.assert_called_once_with(("localhost", 6666))

    def test_close(self):
        self.client.close()
        self.client.socket.close.assert_called_once_with()

    def test_send(self):
        self.client.socket.recv.return_value = "thanks"

        result = self.client.send("foobar\n")
        self.assertEqual(result, "thanks")

        self.client.socket.send.assert_called_once_with("foobar\n")
        self.client.socket.recv.assert_called_once_with(4096)

    def test_send_message_unicode(self):
        self.client.socket.recv.return_value = "thanks"

        result = self.client.send_message(u"foobar")
        self.assertEqual(result, "thanks")

        self.client.socket.send.assert_called_once_with(b"\x0bfoobar\x1c\x0d")

    def test_send_message_bytestring(self):
        self.client.socket.recv.return_value = "thanks"

        result = self.client.send_message(b"foobar")
        self.assertEqual(result, "thanks")

        self.client.socket.send.assert_called_once_with(b"\x0bfoobar\x1c\x0d")

    def test_send_message_hl7_message(self):
        self.client.socket.recv.return_value = "thanks"

        message = hl7.parse(r"MSH|^~\&|GHH LAB|ELAB")

        result = self.client.send_message(message)
        self.assertEqual(result, "thanks")

        self.client.socket.send.assert_called_once_with(
            b"\x0bMSH|^~\\&|GHH LAB|ELAB\r\x1c\x0d"
        )

    def test_context_manager(self):
        with MLLPClient("localhost", 6666) as client:
            client.send("hello world")

        self.client.socket.send.assert_called_once_with("hello world")
        self.client.socket.close.assert_called_once_with()

    def test_context_manager_exception(self):
        with self.assertRaises(Exception):
            with MLLPClient("localhost", 6666):
                raise Exception()

        # socket.close should be called via the with statement
        self.client.socket.close.assert_called_once_with()


class MLLPSendTest(TestCase):
    def setUp(self):
        # patch to avoid touching sys and socket
        self.socket_patch = patch("hl7.client.socket.socket")
        self.mock_socket = self.socket_patch.start()
        self.mock_socket().recv.return_value = "thanks"

        self.stdout_patch = patch("hl7.client.stdout")
        self.mock_stdout = self.stdout_patch.start()

        self.stdin_patch = patch("hl7.client.stdin")
        self.mock_stdin = self.stdin_patch.start()

        self.stderr_patch = patch("hl7.client.stderr")
        self.mock_stderr = self.stderr_patch.start()

        self.exit_patch = patch("hl7.client.sys.exit")
        self.mock_exit = self.exit_patch.start()

        # we need a temporary directory
        self.dir = mkdtemp()
        self.write(SB + b"foobar" + EB + CR)

        self.option_values = Values(
            {
                "port": 6661,
                "filename": os.path.join(self.dir, "test.hl7"),
                "verbose": True,
                "loose": False,
                "version": False,
            }
        )

        self.options_patch = patch("hl7.client.OptionParser")
        option_parser = self.options_patch.start()
        self.mock_options = Mock()
        option_parser.return_value = self.mock_options
        self.mock_options.parse_args.return_value = (self.option_values, ["localhost"])

    def tearDown(self):
        # unpatch
        self.socket_patch.stop()
        self.options_patch.stop()
        self.stdout_patch.stop()
        self.stdin_patch.stop()
        self.stderr_patch.stop()
        self.exit_patch.stop()

        # clean up the temp directory
        rmtree(self.dir)

    def write(self, content, path="test.hl7"):
        with open(os.path.join(self.dir, path), "wb") as f:
            f.write(content)

    def test_send(self):
        mllp_send()

        self.mock_socket().connect.assert_called_once_with(("localhost", 6661))
        self.mock_socket().send.assert_called_once_with(SB + b"foobar" + EB + CR)
        self.mock_stdout.assert_called_once_with("thanks")
        self.assertFalse(self.mock_exit.called)

    def test_send_multiple(self):
        self.mock_socket().recv.return_value = "thanks"
        self.write(SB + b"foobar" + EB + CR + SB + b"hello" + EB + CR)

        mllp_send()

        self.assertEqual(
            self.mock_socket().send.call_args_list[0][0][0], SB + b"foobar" + EB + CR
        )
        self.assertEqual(
            self.mock_socket().send.call_args_list[1][0][0], SB + b"hello" + EB + CR
        )

    def test_leftover_buffer(self):
        self.write(SB + b"foobar" + EB + CR + SB + b"stuff")

        self.assertRaises(MLLPException, mllp_send)

        self.mock_socket().send.assert_called_once_with(SB + b"foobar" + EB + CR)

    def test_quiet(self):
        self.option_values.verbose = False

        mllp_send()

        self.mock_socket().send.assert_called_once_with(SB + b"foobar" + EB + CR)
        self.assertFalse(self.mock_stdout.called)

    def test_port(self):
        self.option_values.port = 7890

        mllp_send()

        self.mock_socket().connect.assert_called_once_with(("localhost", 7890))

    def test_stdin(self):
        self.option_values.filename = None
        self.mock_stdin.return_value = FakeStream()

        mllp_send()

        self.mock_socket().send.assert_called_once_with(SB + b"hello" + EB + CR)

    def test_loose_no_stdin(self):
        self.option_values.loose = True
        self.option_values.filename = None
        self.mock_stdin.return_value = FakeStream()

        mllp_send()

        self.assertFalse(self.mock_socket().send.called)
        self.mock_stderr().write.assert_called_with("--loose requires --file\n")
        self.mock_exit.assert_called_with(1)

    def test_loose_windows_newline(self):
        self.option_values.loose = True
        self.write(SB + b"MSH|^~\\&|foo\r\nbar\r\n" + EB + CR)

        mllp_send()

        self.mock_socket().send.assert_called_once_with(
            SB + b"MSH|^~\\&|foo\rbar" + EB + CR
        )

    def test_loose_unix_newline(self):
        self.option_values.loose = True
        self.write(SB + b"MSH|^~\\&|foo\nbar\n" + EB + CR)

        mllp_send()

        self.mock_socket().send.assert_called_once_with(
            SB + b"MSH|^~\\&|foo\rbar" + EB + CR
        )

    def test_loose_no_mllp_characters(self):
        self.option_values.loose = True
        self.write(b"MSH|^~\\&|foo\r\nbar\r\n")

        mllp_send()

        self.mock_socket().send.assert_called_once_with(
            SB + b"MSH|^~\\&|foo\rbar" + EB + CR
        )

    def test_loose_send_mutliple(self):
        self.option_values.loose = True
        self.mock_socket().recv.return_value = "thanks"
        self.write(b"MSH|^~\\&|1\r\nOBX|1\r\nMSH|^~\\&|2\r\nOBX|2\r\n")

        mllp_send()

        self.assertEqual(
            self.mock_socket().send.call_args_list[0][0][0],
            SB + b"MSH|^~\\&|1\rOBX|1" + EB + CR,
        )
        self.assertEqual(
            self.mock_socket().send.call_args_list[1][0][0],
            SB + b"MSH|^~\\&|2\rOBX|2" + EB + CR,
        )

    def test_version(self):
        self.option_values.version = True

        mllp_send()

        self.assertFalse(self.mock_socket().connect.called)
        self.mock_stdout.assert_called_once_with(str(hl7_version))


class FakeStream(object):
    count = 0

    def read(self, buf):
        self.count += 1
        if self.count == 1:
            return SB + b"hello" + EB + CR
        else:
            return b""
