import io
import logging
import os.path
import socket
import sys
import time
import typing
from argparse import ArgumentParser

import hl7
from hl7.exceptions import CLIException, MLLPException

SB = b"\x0b"  # <SB>, vertical tab
EB = b"\x1c"  # <EB>, file separator
CR = b"\x0d"  # <CR>, \r

FF = b"\x0c"  # <FF>, new page form feed

RECV_BUFFER = 4096

log = logging.getLogger(__name__)


class MLLPClient(object):
    """
    A basic, blocking, HL7 MLLP client based upon :py:mod:`socket`.

    MLLPClient implements two methods for sending data to the server.

    * :py:meth:`MLLPClient.send` for raw data that already is wrapped in the
      appropriate MLLP container (e.g. *<SB>message<EB><CR>*).
    * :py:meth:`MLLPClient.send_message` will wrap the message in the MLLP
      container

    Can be used by the ``with`` statement to ensure :py:meth:`MLLPClient.close`
    is called::

        with MLLPClient(host, port) as client:
            client.send_message('MSH|...')

    MLLPClient takes optional parameters:

    * ``encoding``, defaults to UTF-8, for encoding unicode messages [#]_.
    * ``timeout`` in seconds, timeout for socket operations [_t]_.
    * ``deadline`` in seconds, will be used by the client to determine how long it should wait for full response.

    .. [#] http://wiki.hl7.org/index.php?title=Character_Set_used_in_v2_messages
    .. [_t] https://docs.python.org/3/library/socket.html#socket.socket.settimeout
    """

    def __init__(self, host, port, encoding="utf-8", timeout=10, deadline=3):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.encoding = encoding
        self.timeout = timeout  # seconds for socket timeout
        self.deadline = deadline  # seconds for max time client will wait for a response

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, trackeback):
        self.close()

    def close(self):
        """Release the socket connection"""
        self.socket.close()

    def send_message(self, message: typing.Union[bytes, str, hl7.Message]) -> bytes:
        """Wraps a byte string, unicode string, or :py:class:`hl7.Message`
        in a MLLP container and send the message to the server

        If message is a byte string, we assume it is already encoded properly.
        If message is unicode or  :py:class:`hl7.Message`, it will be encoded
        according to  :py:attr:`hl7.client.MLLPClient.encoding`

        """
        if isinstance(message, bytes):
            # Assume we have the correct encoding
            binary = message
        else:
            # Encode the unicode message into a bytestring
            if isinstance(message, hl7.Message):
                message = str(message)
            binary = message.encode(self.encoding)

        # wrap in MLLP message container
        data = SB + binary + EB + CR
        return self.send(data)

    def send(self, data: bytes) -> bytes:
        """Low-level, direct access to the socket.send (data must be already
        wrapped in an MLLP container).  Blocks until the server returns.
        """
        # upload the data
        log.debug(f"sending {(data,)}")
        self.socket.send(data)
        # wait for the ACK/NACK
        self.socket.settimeout(self.timeout)
        buff = b""
        # the whole message should be received within this deadline
        deadline = time.time() + self.deadline

        # This will read data until deadline is reached.
        # some HL7 counterparts may send responses in chunks, so we should wait some
        # and read from the socket until we probably receive full message.
        # timeout/deadline are configurable on client creation.
        while deadline > time.time():
            try:
                data = self.socket.recv(RECV_BUFFER)
            except TimeoutError:
                data = None
            if data is not None:
                buff += data
            # received LLP end markers
            if buff.endswith(EB + CR):
                break
        log.debug(f"received {(buff,)}")
        return self.clean(buff)

    def clean(self, data: bytes) -> bytes:
        """Removes LLP bytes from data"""
        data = data.lstrip(SB)
        data = data.rstrip(EB + CR)
        return data


# wrappers to make testing easier
def stdout(content):
    # In Python 3, can't write bytes via sys.stdout.write
    #   http://bugs.python.org/issue18512
    if isinstance(content, bytes):
        out = sys.stdout.buffer
        newline = b"\n"
    else:
        out = sys.stdout
        newline = "\n"

    out.write(content + newline)


def stdin():
    return sys.stdin


def stderr():
    return sys.stderr


def read_stream(stream):
    """Buffer the stream and yield individual, stripped messages"""
    _buffer = b""

    while True:
        data = stream.read(RECV_BUFFER)
        if not data:
            break
        if isinstance(data, str):
            data = data.encode("utf-8")
        # usually should be broken up by EB, but I have seen FF separating
        # messages
        messages = (_buffer + data).split(EB if FF not in data else FF)

        # whatever is in the last chunk is an uncompleted message, so put back
        # into the buffer
        _buffer = messages.pop(-1)

        for m in messages:
            yield m.strip(SB + CR)

    if len(_buffer.strip()) > 0:
        raise MLLPException("buffer not terminated: %s" % _buffer)


def read_loose(stream):
    """Turn a HL7-like blob of text into a real HL7 messages"""
    # look for the START_BLOCK to delineate messages
    START_BLOCK = rb"MSH|^~\&|"

    # load all the data
    data = stream.read()

    # Take out all the typical MLLP separators. In Python 3, iterating
    # through a bytestring returns ints, so we need to filter out the int
    # versions of the separators, then convert back from a list of ints to
    # a bytestring.
    # WARNING: There is an assumption here that we can treat the data as single bytes
    #   when filtering out the separators.
    separators = [bs[0] for bs in [EB, FF, SB]]
    data = bytes(b for b in data if b not in separators)
    # Windows & Unix new lines to segment separators
    data = data.replace(b"\r\n", b"\r").replace(b"\n", b"\r")

    for m in data.split(START_BLOCK):
        if not m:
            # the first element will not have any data from the split
            continue

        # strip any trailing whitespace
        m = m.strip(CR + b"\n ")

        # re-insert the START_BLOCK, which was removed via the split
        yield START_BLOCK + m


def mllp_send(in_args=None):
    """Command line tool to send messages to an MLLP server"""
    # set up the command line options
    in_args = in_args or sys.argv
    script_name = os.path.basename(in_args[0])
    parser = ArgumentParser(usage=script_name + " [options] <server>")
    parser.add_argument("host", action="store", nargs=1, help="Host to connect to")
    parser.add_argument(
        "--version",
        action="store_true",
        dest="version",
        help="print current version and exit",
    )
    parser.add_argument(
        "-p",
        "--port",
        action="store",
        type=int,
        required=False,
        dest="port",
        default=6661,
        help="port to connect to",
    )
    parser.add_argument(
        "-f",
        "--file",
        required=False,
        dest="filename",
        default=None,
        help="read from FILE instead of stdin",
        metavar="FILE",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        default=True,
        help="do not print status messages to stdout",
    )
    parser.add_argument(
        "--loose",
        action="store_true",
        dest="loose",
        help=(
            "allow file to be a HL7-like object (\\r\\n instead "
            "of \\r). Requires that messages start with "
            '"MSH|^~\\&|". Requires --file option (no stdin)'
        ),
    )
    parser.add_argument(
        "--timeout",
        action="store",
        dest="timeout",
        required=False,
        default=10,
        type=float,
        help="number of seconds for socket operations to timeout",
    )
    parser.add_argument(
        "--deadline",
        action="store",
        required=False,
        dest="deadline",
        default=3,
        type=float,
        help="number of seconds for the client to receive full response",
    )

    args = parser.parse_args(in_args[1:])
    if args.version:
        import hl7

        stdout(hl7.__version__)
        return

    host = args.host[0]

    log.setLevel(logging.INFO)
    if args.verbose:
        log.setLevel(logging.DEBUG)

    if args.filename is not None:
        # Previously set stream to the open() handle, but then we did not
        # close the open file handle.  This new approach consumes the entire
        # file into memory before starting to process, which is not required
        # or ideal, since we can handle a stream
        with open(args.filename, "rb") as f:
            stream = io.BytesIO(f.read())
    else:
        if args.loose:
            stderr().write("--loose requires --file\n")
            raise CLIException(1)

        stream = stdin()
    with MLLPClient(
        host, args.port, deadline=args.deadline, timeout=args.timeout
    ) as client:
        message_stream = read_stream(stream) if not args.loose else read_loose(stream)
        for message in message_stream:
            result = client.send_message(message)
            if args.verbose:
                stdout(result)


if __name__ == "__main__":
    try:
        mllp_send(sys.argv)
    except CLIException as err:
        sys.exit(err.exit_code)
