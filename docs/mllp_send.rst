===================================
``mllp_send`` - MLLP network client
===================================


python-hl7 features a simple network client, ``mllp_send``, which reads HL7
messages from a file or ``sys.stdin`` and posts them to an MLLP server.
``mllp_send`` is a command-line wrapper around 
:py:class:`hl7.client.MLLPClient`.  ``mllp_send`` is a useful tool for
testing HL7 interfaces or resending logged messages::

    $ mllp_send --file sample.hl7 --port 6661 mirth.example.com
    MSH|^~\&|LIS|Example|Hospital|Mirth|20111207105244||ACK^A01|A234244|P|2.3.1|
    MSA|AA|234242|Message Received Successfully|


Usage
=====
::

    Usage: mllp_send [options] <server>

    Options:
      -h, --help            show this help message and exit
      --version             print current version and exit
      -p PORT, --port=PORT  port to connect to
      -f FILE, --file=FILE  read from FILE instead of stdin
      -q, --quiet           do not print status messages to stdout
      --loose               allow file to be a HL7-like object (\r\n instead of
                            \r). Requires that messages start with "MSH|^~\&|".
                            Requires --file option (no stdin)

Input Format
============

By default, ``mllp_send`` expects the ``FILE`` or stdin input to be a properly
formatted HL7 message (carriage returns separating segments) wrapped in a MLLP
stream (``<SB>message1<EB><CR><SB>message2<EB><CR>...``).

However, it is common, especially if the file has been manually edited in
certain text editors, that the ASCII control characters will be lost and the
carriage returns will be replaced with the platform's default line endings.
In this case, ``mllp_send`` provides the ``--loose`` option, which attempts
to take something that "looks like HL7" and convert it into a proper HL7
message..


Additional Resources
====================

 * http://python-hl7.readthedocs.org
