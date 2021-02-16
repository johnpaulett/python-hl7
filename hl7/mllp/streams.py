import warnings
from asyncio import (
    LimitOverrunError,
    StreamReader,
    StreamReaderProtocol,
    StreamWriter,
    get_event_loop,
    iscoroutine,
)
from asyncio.streams import _DEFAULT_LIMIT

from hl7.mllp.exceptions import InvalidBlockError
from hl7.parser import parse as hl7_parse

START_BLOCK = b"\x0b"
END_BLOCK = b"\x1c"
CARRIAGE_RETURN = b"\x0d"


async def open_hl7_connection(
    host=None,
    port=None,
    *,
    loop=None,
    limit=_DEFAULT_LIMIT,
    encoding=None,
    encoding_errors=None,
    **kwds
):
    """A wrapper for `loop.create_connection()` returning a (reader, writer) pair.

    The reader returned is a :py:class:`hl7.mllp.HL7StreamReader` instance; the writer is a
    :py:class:`hl7.mllp.HL7StreamWriter` instance.

    The arguments are all the usual arguments to create_connection()
    except `protocol_factory`; most common are positional `host` and `port`,
    with various optional keyword arguments following.

    Additional optional keyword arguments are `loop` (to set the event loop
    instance to use), `limit` (to set the buffer limit passed to the
    :py:class:`hl7.mllp.HL7StreamReader`), `encoding` (to set the encoding on the :py:class:`hl7.mllp.HL7StreamReader`
    and :py:class:`hl7.mllp.HL7StreamWriter`) and `encoding_errors` (to set the encoding_errors on the :py:class:`hl7.mllp.HL7StreamReader`
    and :py:class:`hl7.mllp.HL7StreamWriter`).
    """
    if loop is None:
        loop = get_event_loop()
    else:
        warnings.warn(
            "The loop argument is deprecated since Python 3.8, "
            "and scheduled for removal in Python 3.10.",
            DeprecationWarning,
            stacklevel=2,
        )
    reader = HL7StreamReader(
        limit=limit, loop=loop, encoding=encoding, encoding_errors=encoding_errors
    )
    protocol = HL7StreamProtocol(
        reader, loop=loop, encoding=encoding, encoding_errors=encoding_errors
    )
    transport, _ = await loop.create_connection(lambda: protocol, host, port, **kwds)
    writer = HL7StreamWriter(
        transport, protocol, reader, loop, encoding, encoding_errors
    )
    return reader, writer


async def start_hl7_server(
    client_connected_cb,
    host=None,
    port=None,
    *,
    loop=None,
    limit=_DEFAULT_LIMIT,
    encoding=None,
    encoding_errors=None,
    **kwds
):
    """Start a socket server, call back for each client connected.

    The first parameter, `client_connected_cb`, takes two parameters:
    `client_reader`, `client_writer`.  `client_reader` is a
    :py:class:`hl7.mllp.HL7StreamReader` object, while `client_writer`
    is a :py:class:`hl7.mllp.HL7StreamWriter` object.  This
    parameter can either be a plain callback function or a coroutine;
    if it is a coroutine, it will be automatically converted into a
    `Task`.

    The rest of the arguments are all the usual arguments to
    `loop.create_server()` except `protocol_factory`; most common are
    positional `host` and `port`, with various optional keyword arguments
    following.

    The return value is the same as `loop.create_server()`.
    Additional optional keyword arguments are `loop` (to set the event loop
    instance to use) and `limit` (to set the buffer limit passed to the
    StreamReader).

    The return value is the same as `loop.create_server()`, i.e. a
    `Server` object which can be used to stop the service.
    """
    if loop is None:
        loop = get_event_loop()
    else:
        warnings.warn(
            "The loop argument is deprecated since Python 3.8, "
            "and scheduled for removal in Python 3.10.",
            DeprecationWarning,
            stacklevel=2,
        )

    def factory():
        reader = HL7StreamReader(
            limit=limit, loop=loop, encoding=encoding, encoding_errors=encoding_errors
        )
        protocol = HL7StreamProtocol(
            reader,
            client_connected_cb,
            loop=loop,
            encoding=encoding,
            encoding_errors=encoding_errors,
        )
        return protocol

    return await loop.create_server(factory, host, port, **kwds)


class MLLPStreamReader(StreamReader):
    def __init__(self, limit=_DEFAULT_LIMIT, loop=None):
        super().__init__(limit, loop)

    async def readblock(self):
        """Read a chunk of data from the stream until the block termination
        separator (b'\x1c\x0d') are found.

        On success, the data and separator will be removed from the
        internal buffer (consumed). Returned data will not include the
        separator at the end or the MLLP start block character (b'\x0b') at the
        beginning.

        Configured stream limit is used to check result. Limit sets the
        maximal length of data that can be returned, not counting the
        separator.

        If an EOF occurs and the complete separator is still not found,
        an IncompleteReadError exception will be raised, and the internal
        buffer will be reset.  The IncompleteReadError.partial attribute
        may contain the separator partially.

        If limit is reached, ValueError will be raised. In that case, if
        block termination separator was found, complete line including separator
        will be removed from internal buffer. Else, internal buffer will be cleared. Limit is
        compared against part of the line without separator.

        If the block is invalid (missing required start block character) and InvalidBlockError
        will be raised.

        If stream was paused, this function will automatically resume it if
        needed.
        """
        sep = END_BLOCK + CARRIAGE_RETURN
        seplen = len(sep)
        try:
            block = await self.readuntil(sep)
        except LimitOverrunError as loe:
            if self._buffer.startswith(sep, loe.consumed):
                del self._buffer[: loe.consumed + seplen]
            else:
                self._buffer.clear()
            self._maybe_resume_transport()
            raise ValueError(loe.args[0])
        if not block or block[0:1] != START_BLOCK:
            raise InvalidBlockError(
                "Block does not begin with Start Block character <VT>"
            )
        return block[1:-2]


class MLLPStreamWriter(StreamWriter):
    def __init__(self, transport, protocol, reader, loop):
        super().__init__(transport, protocol, reader, loop)

    def writeblock(self, data):
        """Write a block of data to the stream,
        encapsulating the block with b'\x0b' at the beginning
        and b'\x1c\x0d' at the end.
        """
        self.write(START_BLOCK + data + END_BLOCK + CARRIAGE_RETURN)


class HL7StreamProtocol(StreamReaderProtocol):
    def __init__(
        self,
        stream_reader,
        client_connected_cb=None,
        loop=None,
        encoding=None,
        encoding_errors=None,
    ):
        super().__init__(stream_reader, client_connected_cb, loop)
        self._encoding = encoding
        self._encoding_errors = encoding_errors

    def connection_made(self, transport):
        if self._reject_connection:
            context = {
                "message": (
                    "An open stream was garbage collected prior to "
                    "establishing network connection; "
                    'call "stream.close()" explicitly.'
                )
            }
            if self._source_traceback:
                context["source_traceback"] = self._source_traceback
            self._loop.call_exception_handler(context)
            transport.abort()
            return
        self._transport = transport
        reader = self._stream_reader
        if reader is not None:
            reader.set_transport(transport)
        self._over_ssl = transport.get_extra_info("sslcontext") is not None
        if self._client_connected_cb is not None:
            self._stream_writer = HL7StreamWriter(
                transport,
                self,
                reader,
                self._loop,
                self._encoding,
                self._encoding_errors,
            )
            res = self._client_connected_cb(reader, self._stream_writer)
            if iscoroutine(res):
                self._loop.create_task(res)
            self._strong_reader = None


class HL7StreamReader(MLLPStreamReader):
    def __init__(
        self, limit=_DEFAULT_LIMIT, loop=None, encoding=None, encoding_errors=None
    ):
        super().__init__(limit=limit, loop=loop)
        self.encoding = encoding
        self.encoding_errors = encoding_errors

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        if encoding and not isinstance(encoding, str):
            raise TypeError("encoding must be a str or None")
        self._encoding = encoding or "ascii"

    @property
    def encoding_errors(self):
        return self._encoding_errors

    @encoding_errors.setter
    def encoding_errors(self, encoding_errors):
        if encoding_errors and not isinstance(encoding_errors, str):
            raise TypeError("encoding_errors must be a str or None")
        self._encoding_errors = encoding_errors or "strict"

    async def readmessage(self):
        """Reads a full HL7 message from the stream.

        This will return an :py:class:`hl7.Message`.

        If `limit` is reached, `ValueError` will be raised. In that case, if
        block termination separator was found, complete line including separator
        will be removed from internal buffer. Else, internal buffer will be cleared. Limit is
        compared against part of the line without separator.

        If an invalid MLLP block is encountered, :py:class:`hl7.mllp.InvalidBlockError` will be
        raised.
        """
        block = await self.readblock()
        return hl7_parse(block.decode(self.encoding, self.encoding_errors))


class HL7StreamWriter(MLLPStreamWriter):
    def __init__(
        self, transport, protocol, reader, loop, encoding=None, encoding_errors=None
    ):
        super().__init__(transport, protocol, reader, loop)
        self.encoding = encoding
        self.encoding_errors = encoding_errors

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        if encoding and not isinstance(encoding, str):
            raise TypeError("encoding must be a str or None")
        self._encoding = encoding or "ascii"

    @property
    def encoding_errors(self):
        return self._encoding_errors

    @encoding_errors.setter
    def encoding_errors(self, encoding_errors):
        if encoding_errors and not isinstance(encoding_errors, str):
            raise TypeError("encoding_errors must be a str or None")
        self._encoding_errors = encoding_errors or "strict"

    def writemessage(self, message):
        """Writes an :py:class:`hl7.Message` to the stream."""
        self.writeblock(str(message).encode(self.encoding, self.encoding_errors))
