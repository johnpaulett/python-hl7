from optparse import OptionParser

import os.path
import socket
import sys


SB = '\x0b' #<SB>, vertical tab
EB = '\x1c' #<EB>, file separator
CR = '\x0d' #<CR>, \r

FF = '\x0c' # <FF>, new page form feed

RECV_BUFFER = 4096

class MLLPException(Exception): pass

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

    """
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, trackeback):
        self.close()

    def close(self):
        """Release the socket connection"""
        self.socket.close()

    def send_message(self, message):
        """Wraps a str, unicode, or :py:cls:`hl7.Message` in a MLLP container
        and send the message to the server
        """
        # wrap in MLLP message container
        data = SB + unicode(message) + EB + CR
        # TODO consider encoding (e.g. UTF-8)
        return self.send(data)

    def send(self, data):
        """Low-level, direct access to the socket.send (data must be already
        wrapped in an MLLP container).  Blocks until the server returns.
        """
        # upload the data
        self.socket.send(data)
        # wait for the ACK/NACK
        return self.socket.recv(RECV_BUFFER)


# wrappers to make testing easier
def stdout(content):
    sys.stdout.write(content + '\n')

def stdin():
    return sys.stdin

def stderr():
    return sys.stderr

def read_stream(stream):
    """Buffer the stream and yield individual, stripped messages"""
    _buffer = ''

    while True:
        data = stream.read(RECV_BUFFER)
        if data == '':
            break
        # usually should be broken up by EB, but I have seen FF separating
        # messages
        messages = (_buffer + data).split(EB if FF not in data else FF)

        # whatever is in the last chunk is an uncompleted message, so put back
        # into the buffer
        _buffer = messages.pop(-1)

        for m in messages:
            yield m.strip(SB+CR)

    if len(_buffer.strip()) > 0:
        raise MLLPException('buffer not terminated: %s' % _buffer)

def read_loose(stream):
    """Turn a HL7-like blob of text into a real HL7 messages"""
    # look for the START_BLOCK to delineate messages
    START_BLOCK = r'MSH|^~\&|'

    # load all the data
    data = stream.read()

    # take out all the the typical MLLP separators
    data = ''.join([c for c in data if c not in [EB, FF, SB]])

    # Windows & Unix new lines to segment separators
    data = data.replace('\r\n', '\r').replace('\n', '\r')

    for m in data.split(START_BLOCK):
        if not m:
            # the first element will not have any data from the split
            continue

        # strip any trailing whitespace
        m = m.strip(CR+'\n ')

        # re-insert the START_BLOCK, which was removed via the split
        yield START_BLOCK + m

def mllp_send():
    """Command line tool to send messages to an MLLP server"""
    # set up the command line options
    script_name = os.path.basename(sys.argv[0])
    parser = OptionParser(usage=script_name + ' [options] <server>')
    parser.add_option('--version',
                  action='store_true', dest='version', default=False,
                  help='print current version and exit')
    parser.add_option('-p', '--port',
                  action='store', type='int', dest='port', default=6661,
                  help='port to connect to')
    parser.add_option('-f', '--file', dest='filename',
                  help='read from FILE instead of stdin', metavar='FILE')
    parser.add_option('-q', '--quiet',
                  action='store_true', dest='verbose', default=True,
                  help='do not print status messages to stdout')
    parser.add_option('--loose',
                  action='store_true', dest='loose', default=False,
                  help='allow file to be a HL7-like object (\\r\\n instead ' \
                          + 'of \\r). Requires that messages start with ' \
                          + '"MSH|^~\\&|". Requires --file option (no stdin)')

    (options, args) = parser.parse_args()

    if options.version:
        import hl7
        stdout(hl7.__version__)
        return

    if len(args) == 1:
        host = args[0]
    else:
        # server not present
        parser.print_usage()
        stderr().write('server required\n')
        return

    if options.filename is not None:
        stream = open(options.filename, 'rb') #FIXME with_statement
    else:
        if options.loose:
            stderr().write('--loose requires --file\n')
            return
        stream = stdin()

    with MLLPClient(host, options.port) as client:
        message_stream = read_stream(stream) \
                         if not options.loose \
                         else read_loose(stream)

        for message in message_stream:
            result = client.send_message(message)
            if options.verbose:
                stdout(result)


if __name__ == '__main__':
    mllp_send()
