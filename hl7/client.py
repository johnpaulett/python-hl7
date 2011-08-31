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

def mllp_send():
    """Command line tool to send messages to an MLLP server"""
    # set up the command line options
    script_name = os.path.basename(sys.argv[0])
    parser = OptionParser(usage=script_name + ' [options] <server>')
    parser.add_option('-p', '--port',
                  action='store', type='int', dest='port', default=6661,
                  help='port to connect to')
    parser.add_option('-f', '--file', dest='filename',
                  help='read from FILE instead of stdin', metavar='FILE')
    parser.add_option('-q', '--quiet',
                  action='store_true', dest='verbose', default=True,
                  help='do not print status messages to stdout')

    (options, args) = parser.parse_args()
    if len(args) == 1:
        host = args[0]
    else:
        # server not present
        parser.print_usage()
        sys.stderr.write('server required\n')
        return

    if options.filename is not None:
        stream = open(options.filename, 'rb') #FIXME with_statement
    else:
        stream = stdin()

    with MLLPClient(host, options.port) as client:
        for message in read_stream(stream):
            result = client.send_message(message)
            if options.verbose:
                stdout(result)


if __name__ == '__main__':
    mllp_send()
