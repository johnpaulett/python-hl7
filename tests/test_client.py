import os
import socket
import threading
from argparse import Namespace
from shutil import rmtree
from tempfile import mkdtemp
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, call, patch

import hl7
from hl7 import __version__ as hl7_version
from hl7.client import (
    CR,
    EB,
    SB,
    MLLPClient,
    MLLPException,
    _positive_timeout,
    mllp_send,
)


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

    def test_no_timeout_by_default(self):
        self.assertFalse(self.client.socket.settimeout.called)

    def test_timeout_set_before_connect(self):
        self.mock_socket.reset_mock()

        MLLPClient("localhost", 6666, timeout=2.5)

        self.assertEqual(
            self.mock_socket.return_value.mock_calls,
            [call.settimeout(2.5), call.connect(("localhost", 6666))],
        )

    def test_socket_closed_when_connect_times_out(self):
        self.mock_socket.reset_mock()
        self.mock_socket.return_value.connect.side_effect = socket.timeout

        with self.assertRaises(socket.timeout):
            MLLPClient("localhost", 6666, timeout=1)

        self.mock_socket.return_value.close.assert_called_once_with()

    def test_socket_closed_when_connect_refused(self):
        self.mock_socket.reset_mock()
        self.mock_socket.return_value.connect.side_effect = ConnectionRefusedError

        with self.assertRaises(ConnectionRefusedError):
            MLLPClient("localhost", 6666)

        self.mock_socket.return_value.close.assert_called_once_with()

    def test_close(self):
        self.client.close()
        self.client.socket.close.assert_called_once_with()

    def test_send(self):
        self.client.socket.recv.return_value = "thanks"

        result = self.client.send("foobar\n")
        self.assertEqual(result, "thanks")

        self.client.socket.sendall.assert_called_once_with("foobar\n")
        self.client.socket.recv.assert_called_once_with(4096)

    def test_send_message_unicode(self):
        self.client.socket.recv.return_value = "thanks"

        result = self.client.send_message("foobar")
        self.assertEqual(result, "thanks")

        self.client.socket.sendall.assert_called_once_with(b"\x0bfoobar\x1c\x0d")

    def test_send_message_bytestring(self):
        self.client.socket.recv.return_value = "thanks"

        result = self.client.send_message(b"foobar")
        self.assertEqual(result, "thanks")

        self.client.socket.sendall.assert_called_once_with(b"\x0bfoobar\x1c\x0d")

    def test_send_message_hl7_message(self):
        self.client.socket.recv.return_value = "thanks"

        message = hl7.parse(r"MSH|^~\&|GHH LAB|ELAB")

        result = self.client.send_message(message)
        self.assertEqual(result, "thanks")

        self.client.socket.sendall.assert_called_once_with(
            b"\x0bMSH|^~\\&|GHH LAB|ELAB\r\x1c\x0d"
        )

    def test_context_manager(self):
        with MLLPClient("localhost", 6666) as client:
            client.send("hello world")

        self.client.socket.sendall.assert_called_once_with("hello world")
        self.client.socket.close.assert_called_once_with()

    def test_context_manager_exception(self):
        with self.assertRaises(Exception):
            with MLLPClient("localhost", 6666):
                raise Exception()

        # socket.close should be called via the with statement
        self.client.socket.close.assert_called_once_with()


class MLLPClientTimeoutTest(TestCase):
    def setUp(self):
        # real loopback server that accepts a connection but never replies
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(self.server.close)
        self.server.bind(("127.0.0.1", 0))
        self.server.listen(1)
        self.server.settimeout(5)
        self.port = self.server.getsockname()[1]

        self.done = threading.Event()
        self.thread = threading.Thread(target=self.accept_and_ignore, daemon=True)
        self.thread.start()
        # cleanups run in reverse: release the thread, join it, close server
        self.addCleanup(self.thread.join, 5)
        self.addCleanup(self.done.set)

    def accept_and_ignore(self):
        try:
            conn, _ = self.server.accept()
        except OSError:
            return
        with conn:
            self.done.wait(5)

    def test_send_message_times_out(self):
        with MLLPClient("127.0.0.1", self.port, timeout=0.2) as client:
            with self.assertRaises(socket.timeout):
                client.send_message(b"MSH|^~\\&|foo")


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

        self.option_values = Namespace(
            port=6661,
            timeout=None,
            filename=os.path.join(self.dir, "test.hl7"),
            verbose=True,
            loose=False,
            version=False,
            server="localhost",
        )

        self.options_patch = patch("hl7.client.argparse.ArgumentParser")
        option_parser = self.options_patch.start()
        self.mock_options = Mock()
        option_parser.return_value = self.mock_options
        self.mock_options.parse_args.return_value = self.option_values

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
        self.mock_socket().sendall.assert_called_once_with(SB + b"foobar" + EB + CR)
        self.mock_stdout.assert_called_once_with("thanks")
        self.assertFalse(self.mock_exit.called)

    def test_send_multiple(self):
        self.mock_socket().recv.return_value = "thanks"
        self.write(SB + b"foobar" + EB + CR + SB + b"hello" + EB + CR)

        mllp_send()

        self.assertEqual(
            self.mock_socket().sendall.call_args_list[0][0][0], SB + b"foobar" + EB + CR
        )
        self.assertEqual(
            self.mock_socket().sendall.call_args_list[1][0][0], SB + b"hello" + EB + CR
        )

    def test_leftover_buffer(self):
        self.write(SB + b"foobar" + EB + CR + SB + b"stuff")

        self.assertRaises(MLLPException, mllp_send)

        self.mock_socket().sendall.assert_called_once_with(SB + b"foobar" + EB + CR)

    def test_quiet(self):
        self.option_values.verbose = False

        mllp_send()

        self.mock_socket().sendall.assert_called_once_with(SB + b"foobar" + EB + CR)
        self.assertFalse(self.mock_stdout.called)

    def test_port(self):
        self.option_values.port = 7890

        mllp_send()

        self.mock_socket().connect.assert_called_once_with(("localhost", 7890))

    def test_no_timeout(self):
        mllp_send()

        self.assertFalse(self.mock_socket().settimeout.called)

    def test_timeout(self):
        self.option_values.timeout = 2.5

        mllp_send()

        self.mock_socket().settimeout.assert_called_once_with(2.5)

    def test_stdin(self):
        self.option_values.filename = None
        self.mock_stdin.return_value = FakeStream()

        mllp_send()

        self.mock_socket().sendall.assert_called_once_with(SB + b"hello" + EB + CR)

    def test_loose_no_stdin(self):
        self.option_values.loose = True
        self.option_values.filename = None
        self.mock_stdin.return_value = FakeStream()

        mllp_send()

        self.assertFalse(self.mock_socket().sendall.called)
        self.mock_stderr().write.assert_called_with("--loose requires --file\n")
        self.mock_exit.assert_called_with(1)

    def test_loose_windows_newline(self):
        self.option_values.loose = True
        self.write(SB + b"MSH|^~\\&|foo\r\nbar\r\n" + EB + CR)

        mllp_send()

        self.mock_socket().sendall.assert_called_once_with(
            SB + b"MSH|^~\\&|foo\rbar" + EB + CR
        )

    def test_loose_unix_newline(self):
        self.option_values.loose = True
        self.write(SB + b"MSH|^~\\&|foo\nbar\n" + EB + CR)

        mllp_send()

        self.mock_socket().sendall.assert_called_once_with(
            SB + b"MSH|^~\\&|foo\rbar" + EB + CR
        )

    def test_loose_no_mllp_characters(self):
        self.option_values.loose = True
        self.write(b"MSH|^~\\&|foo\r\nbar\r\n")

        mllp_send()

        self.mock_socket().sendall.assert_called_once_with(
            SB + b"MSH|^~\\&|foo\rbar" + EB + CR
        )

    def test_loose_send_mutliple(self):
        self.option_values.loose = True
        self.mock_socket().recv.return_value = "thanks"
        self.write(b"MSH|^~\\&|1\r\nOBX|1\r\nMSH|^~\\&|2\r\nOBX|2\r\n")

        mllp_send()

        self.assertEqual(
            self.mock_socket().sendall.call_args_list[0][0][0],
            SB + b"MSH|^~\\&|1\rOBX|1" + EB + CR,
        )
        self.assertEqual(
            self.mock_socket().sendall.call_args_list[1][0][0],
            SB + b"MSH|^~\\&|2\rOBX|2" + EB + CR,
        )

    def test_version(self):
        self.option_values.version = True

        mllp_send()

        self.assertFalse(self.mock_socket().connect.called)
        self.mock_stdout.assert_called_once_with(str(hl7_version))

    def test_missing_server(self):
        self.option_values.server = None

        mllp_send()

        self.assertFalse(self.mock_socket().connect.called)
        self.mock_options.print_usage.assert_called_once_with()
        self.mock_stderr().write.assert_called_with("server required\n")
        self.mock_exit.assert_called_with(1)

    def test_quiet_cli_option_suppresses_output(self):
        argv = [
            "mllp_send",
            "--file",
            os.path.join(self.dir, "test.hl7"),
            "--quiet",
            "localhost",
        ]
        # stop patched parser to use real CLI parsing
        self.options_patch.stop()
        with patch("hl7.client.sys.argv", argv):
            mllp_send()
        self.assertFalse(self.mock_stdout.called)

    def test_timeout_cli_option(self):
        argv = [
            "mllp_send",
            "--file",
            os.path.join(self.dir, "test.hl7"),
            "--timeout",
            "2.5",
            "localhost",
        ]
        # stop patched parser to use real CLI parsing
        self.options_patch.stop()
        with patch("hl7.client.sys.argv", argv):
            mllp_send()
        self.mock_socket().settimeout.assert_called_once_with(2.5)

    def test_timeout_expiry_raises_and_closes(self):
        self.option_values.timeout = 0.5
        self.mock_socket().recv.side_effect = socket.timeout

        with self.assertRaises(socket.timeout):
            mllp_send()

        self.mock_socket().close.assert_called_once_with()

    def test_invalid_timeout_cli_option_is_rejected(self):
        # stop patched parser to use real CLI parsing
        self.options_patch.stop()
        self.mock_exit.side_effect = SystemExit(2)
        for value in ["0", "-1", "nan", "inf", "soon"]:
            with self.subTest(value=value):
                argv = [
                    "mllp_send",
                    "--file",
                    os.path.join(self.dir, "test.hl7"),
                    "--timeout",
                    value,
                    "localhost",
                ]
                with (
                    patch("hl7.client.sys.argv", argv),
                    patch("sys.stderr", new_callable=StringIO) as err,
                ):
                    with self.assertRaises(SystemExit):
                        mllp_send()
                self.assertIn("timeout", err.getvalue())
                self.assertFalse(self.mock_socket().connect.called)

    def test_positive_timeout_accepts_seconds(self):
        self.assertEqual(_positive_timeout("2.5"), 2.5)
        self.assertEqual(_positive_timeout("10"), 10.0)


class FakeStream:
    count = 0

    def read(self, buf):
        self.count += 1
        if self.count == 1:
            return SB + b"hello" + EB + CR
        else:
            return b""
