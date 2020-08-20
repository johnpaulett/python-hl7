import asyncio
import io
import os.path
import sys
from optparse import OptionParser

import hl7
from hl7.asyncio import open_hl7_connection

SB = b"\x0b"  # <SB>, vertical tab
EB = b"\x1c"  # <EB>, file separator
CR = b"\x0d"  # <CR>, \r

FF = b"\x0c"  # <FF>, new page form feed

RECV_BUFFER = 4096


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
        if data == b"":
            break
        # usually should be broken up by EB, but I have seen FF separating
        # messages
        messages = (_buffer + data).split(EB if FF not in data else FF)

        # whatever is in the last chunk is an uncompleted message, so put back
        # into the buffer
        _buffer = messages.pop(-1)

        for m in messages:
            yield m.strip(SB + CR)

    if len(_buffer.strip()) > 0:
        raise Exception("buffer not terminated: %s" % _buffer)


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


async def mllp_send():
    """Command line tool to send messages to an MLLP server"""
    # set up the command line options
    script_name = os.path.basename(sys.argv[0])
    parser = OptionParser(usage=script_name + " [options] <server>")
    parser.add_option(
        "--version",
        action="store_true",
        dest="version",
        default=False,
        help="print current version and exit",
    )
    parser.add_option(
        "-p",
        "--port",
        action="store",
        type="int",
        dest="port",
        default=6661,
        help="port to connect to",
    )
    parser.add_option(
        "-f",
        "--file",
        dest="filename",
        help="read from FILE instead of stdin",
        metavar="FILE",
    )
    parser.add_option(
        "-q",
        "--quiet",
        action="store_true",
        dest="verbose",
        default=True,
        help="do not print status messages to stdout",
    )
    parser.add_option(
        "--loose",
        action="store_true",
        dest="loose",
        default=False,
        help=(
            "allow file to be a HL7-like object (\\r\\n instead "
            "of \\r). Requires that messages start with "
            '"MSH|^~\\&|". Requires --file option (no stdin)'
        ),
    )

    (options, args) = parser.parse_args()

    if options.version:
        stdout(hl7.__version__)
        return

    if len(args) == 1:
        host = args[0]
    else:
        # server not present
        parser.print_usage()
        stderr().write("server required\n")
        sys.exit(1)
        return  # for testing when sys.exit mocked

    if options.filename is not None:
        # Previously set stream to the open() handle, but then we did not
        # close the open file handle.  This new approach consumes the entire
        # file into memory before starting to process, which is not required
        # or ideal, since we can handle a stream
        with open(options.filename, "rb") as f:
            stream = io.BytesIO(f.read())
    else:
        if options.loose:
            stderr().write("--loose requires --file\n")
            sys.exit(1)
            return  # for testing when sys.exit mocked

        stream = stdin()

    hl7_reader, hl7_writer = await open_hl7_connection(host, options.port)

    for message in read_stream(stream) if not options.loose else read_loose(stream):
        if isinstance(message, (bytes, bytearray)):
            message = message.decode()
        hl7_writer.writemessage(hl7.parse(message))
        await hl7_writer.drain()
        ack = await hl7_reader.readmessage()
        if options.verbose:
            stdout(str(ack))

    hl7_writer.close()
    await hl7_writer.wait_closed()


def run_sender():
    asyncio.run(mllp_send())


if __name__ == "__main__":
    run_sender()
