import asyncio
import asyncio.streams
import sys
from unittest.mock import create_autospec

import hl7
import hl7.mllp

# IsolatedAsyncioTestCase added in 3.8, use backport for older code
if sys.version_info.major <= 3 and sys.version_info.minor < 8:
    from .backports.unittest.async_case import IsolatedAsyncioTestCase
else:
    from unittest import IsolatedAsyncioTestCase


START_BLOCK = b"\x0b"
END_BLOCK = b"\x1c"
CARRIAGE_RETURN = b"\x0d"


class MLLPStreamWriterTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.transport = create_autospec(asyncio.Transport)

    async def asyncSetUp(self):
        self.writer = hl7.mllp.MLLPStreamWriter(
            self.transport,
            create_autospec(asyncio.streams.StreamReaderProtocol),
            create_autospec(hl7.mllp.MLLPStreamReader),
            asyncio.get_running_loop(),
        )

    def test_writeblock(self):
        self.writer.writeblock(b"foobar")
        self.transport.write.assert_called_with(
            START_BLOCK + b"foobar" + END_BLOCK + CARRIAGE_RETURN
        )


class MLLPStreamReaderTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.reader = hl7.mllp.MLLPStreamReader()

    async def test_readblock(self):
        self.reader.feed_data(START_BLOCK + b"foobar" + END_BLOCK + CARRIAGE_RETURN)
        block = await self.reader.readblock()
        self.assertEqual(block, b"foobar")


class HL7StreamWriterTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.transport = create_autospec(asyncio.Transport)

    async def asyncSetUp(self):
        def mock_cb(reader, writer):
            pass

        reader = create_autospec(asyncio.streams.StreamReader)

        self.writer = hl7.mllp.HL7StreamWriter(
            self.transport,
            hl7.mllp.HL7StreamProtocol(reader, mock_cb, asyncio.get_running_loop()),
            reader,
            asyncio.get_running_loop(),
        )

    def test_writemessage(self):
        message = r"MSH|^~\&|LABADT|DH|EPICADT|DH|201301011228||ACK^A01^ACK|HL7ACK00001|P|2.3\r"
        message += "MSA|AA|HL7MSG00001\r"
        hl7_message = hl7.parse(message)
        self.writer.writemessage(hl7_message)
        self.transport.write.assert_called_with(
            START_BLOCK + message.encode() + END_BLOCK + CARRIAGE_RETURN
        )


class HL7StreamReaderTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.reader = hl7.mllp.HL7StreamReader()

    async def test_readblock(self):
        message = r"MSH|^~\&|LABADT|DH|EPICADT|DH|201301011228||ACK^A01^ACK|HL7ACK00001|P|2.3\r"
        message += "MSA|AA|HL7MSG00001\r"
        self.reader.feed_data(
            START_BLOCK + message.encode() + END_BLOCK + CARRIAGE_RETURN
        )
        hl7_message = await self.reader.readmessage()
        self.assertEqual(str(hl7_message), str(hl7.parse(message)))
