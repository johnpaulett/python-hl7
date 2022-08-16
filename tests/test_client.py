import os
import socket
import typing
import logging
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase
from unittest.mock import patch

import hl7
from hl7 import __version__ as hl7_version
from hl7.client import CR, EB, MLLPClient, MLLPException, SB, mllp_send
from hl7.exceptions import CLIException


log = logging.getLogger(__name__)

def return_values_list(*values) -> typing.Iterable[typing.Any]:
    """
    Generates an iterator, which will return each of values and None after values is depleted.

    This helper is used to mock socket.recv() behavior, when no data from the opposite endpoint may result
     in returning None, but still having the socket active.
    :param values:
    :return:
    """

    def _iter(*_values):
        for v in _values:
            yield v
        while True:
            yield None

    return _iter(*values)


class MLLPClientTest(TestCase):
    def setUp(self):
        # use a mock version of socket
        self.socket_patch = patch("hl7.client.socket.socket")
        self.mock_socket = self.socket_patch.start()

        self.client = MLLPClient("localhost", 6666, deadline=0.0001)

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
        # socket.recv returns bytes: https://docs.python.org/3/library/socket.html#socket.socket.recv
        # > Receive data from the socket. The return value is a bytes object representing the data received.
        self.client.socket.recv.side_effect = return_values_list(b"thanks")

        result = self.client.send("foobar\n")
        self.assertEqual(result, b"thanks")

        self.client.socket.send.assert_called_once_with("foobar\n")
        self.client.socket.recv.assert_any_call(4096)

    def test_send_message_unicode(self):
        self.client.socket.recv.side_effect = return_values_list(b"thanks")

        result = self.client.send_message("foobar")
        self.assertEqual(result, b"thanks")

        self.client.socket.send.assert_called_once_with(b"\x0bfoobar\x1c\x0d")

    def test_send_message_bytestring(self):
        self.client.socket.recv.side_effect = return_values_list(b"thanks")

        result = self.client.send_message(b"foobar")
        self.assertEqual(result, b"thanks")

        self.client.socket.send.assert_called_once_with(b"\x0bfoobar\x1c\x0d")

    def test_send_message_hl7_message(self):
        self.client.socket.recv.side_effect = return_values_list(b"thanks")

        message = hl7.parse(r"MSH|^~\&|GHH LAB|ELAB")

        result = self.client.send_message(message)
        self.assertEqual(result, b"thanks")

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
        self.mock_socket().recv.side_effect = return_values_list(b"thanks")

        self.stdout_patch = patch("hl7.client.stdout")
        self.mock_stdout = self.stdout_patch.start()

        self.stdin_patch = patch("hl7.client.stdin")
        self.mock_stdin = self.stdin_patch.start()

        self.stderr_patch = patch("hl7.client.stderr")
        self.mock_stderr = self.stderr_patch.start()

        self.exit_patch = patch("argparse.ArgumentParser.exit")
        self.exit_patch.side_effect = CLIException(2)
        self.mock_exit = self.exit_patch.start()

        # we need a temporary directory
        self.dir = mkdtemp()
        self.write(SB + b"foobar" + EB + CR)

        self.option_values = [
            __name__,
            "--file",
            os.path.join(self.dir, "test.hl7"),
            "--port",
            "6661",
            "--deadline",
            "0.0001",
            "localhost",
        ]

    def _mllp_send(self, args: typing.Optional[typing.List] = None):
        log.debug('calling mllp_send with args: ', args or self.option_values)
        return mllp_send(args or self.option_values)

    def tearDown(self):
        # unpatch
        self.socket_patch.stop()
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
        self._mllp_send()

        self.mock_socket().connect.assert_called_once_with(("localhost", 6661))
        self.mock_socket().send.assert_called_once_with(SB + b"foobar" + EB + CR)
        self.mock_stdout.assert_called_once_with(b"thanks")
        self.assertFalse(self.mock_exit.called)

    def test_send_multiple(self):
        self.mock_socket().recv.side_effect = return_values_list(b"thanks")
        self.write(SB + b"foobar" + EB + CR + SB + b"hello" + EB + CR)

        self._mllp_send()

        self.assertEqual(
            self.mock_socket().send.call_args_list[0][0][0], SB + b"foobar" + EB + CR
        )
        self.assertEqual(
            self.mock_socket().send.call_args_list[1][0][0], SB + b"hello" + EB + CR
        )

    def test_leftover_buffer(self):
        self.write(SB + b"foobar" + EB + CR + SB + b"stuff")

        self.assertRaises(MLLPException, mllp_send, self.option_values)

        self.mock_socket().send.assert_called_once_with(SB + b"foobar" + EB + CR)

    def test_quiet(self):
        options = self.option_values.copy()
        options.append('--quiet')

        self._mllp_send(options)

        self.mock_socket().send.assert_called_once_with(SB + b"foobar" + EB + CR)
        self.assertFalse(self.mock_stdout.called, self.mock_stdout.call_args)

    def test_port(self):
        # replace default port with some exotic value
        options = self.option_values[:4] + ['7890'] + self.option_values[5:]

        self._mllp_send(options)

        self.mock_socket().connect.assert_called_once_with(("localhost", 7890))

    def test_stdin(self):
        # no filename, just stdin
        options = self.option_values.copy()
        options = options[:1] + options[3:]

        self.mock_stdin.return_value = FakeStream()

        self._mllp_send(options)

        self.mock_socket().send.assert_called_once_with(SB + b"hello" + EB + CR)

    def test_loose_no_stdin(self):
        options = self.option_values.copy()
        options.append('--loose')
        # cut out file path
        options = options[:1] + options[3:]
        self.mock_stdin.return_value = FakeStream()

        self.assertRaises(CLIException, self._mllp_send, options)

        self.assertFalse(self.mock_socket().send.called)
        self.mock_stderr().write.assert_called_with("--loose requires --file\n")

    def test_loose_windows_newline(self):
        options = self.option_values.copy()
        options.append('--loose')

        self.write(SB + b"MSH|^~\\&|foo\r\nbar\r\n" + EB + CR)

        self._mllp_send(options)

        self.mock_socket().send.assert_called_once_with(
            SB + b"MSH|^~\\&|foo\rbar" + EB + CR
        )

    def test_loose_unix_newline(self):
        options = self.option_values.copy()
        options.append('--loose')

        self.write(SB + b"MSH|^~\\&|foo\nbar\n" + EB + CR)

        self._mllp_send(options)

        self.mock_socket().send.assert_called_once_with(
            SB + b"MSH|^~\\&|foo\rbar" + EB + CR
        )

    def test_loose_no_mllp_characters(self):
        options = self.option_values.copy()
        options.append('--loose')
        self.write(b"MSH|^~\\&|foo\r\nbar\r\n")

        self._mllp_send(options)

        self.mock_socket().send.assert_called_once_with(
            SB + b"MSH|^~\\&|foo\rbar" + EB + CR
        )

    def test_loose_send_mutliple(self):
        options = self.option_values.copy()
        options.append('--loose')
        self.mock_socket().recv.side_effect = return_values_list(b"thanks")
        self.write(b"MSH|^~\\&|1\r\nOBX|1\r\nMSH|^~\\&|2\r\nOBX|2\r\n")

        self._mllp_send(options)

        self.assertEqual(
            self.mock_socket().send.call_args_list[0][0][0],
            SB + b"MSH|^~\\&|1\rOBX|1" + EB + CR,
        )
        self.assertEqual(
            self.mock_socket().send.call_args_list[1][0][0],
            SB + b"MSH|^~\\&|2\rOBX|2" + EB + CR,
        )

    def test_version(self):

        options = self.option_values
        options.append('--version')

        self._mllp_send(options)

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
