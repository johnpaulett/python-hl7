===================================
``mllp_send`` - MLLP network client
===================================

python-hl7 features a simple network client, ``mllp_send``, which reads HL7
messages from a file or ``sys.stdin`` and posts them to an MLLP server.
``mllp_send`` is a command-line wrapper around
:py:class:`hl7.client.MLLPClient`.

::

    Usage: mllp_send [options] <server>

    Options:
      -h, --help            show this help message and exit
      -p PORT, --port=PORT  port to connect to
      -f FILE, --file=FILE  read from FILE instead of stdin
      -q, --quiet           do not print status messages to stdout
      --loose               allow file to be a HL7-like object (\r\n instead of
                            \r). Can ONLY send 1 message. Requires --file option
                            (no stdin)

For more details, visit http://python-hl7.readthedocs.org
