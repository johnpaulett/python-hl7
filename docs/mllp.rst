MLLP using asyncio
==================

.. versionadded:: 0.4.1

.. note::

   `hl7.mllp` package is currently experimental and subject to change.
   It aims to replace txHL7.

python-hl7 includes classes for building HL7 clients and
servers using asyncio. The underlying protocol for these
clients and servers is MLLP.

The `hl7.mllp` package is designed the same as
the `asyncio.streams` package. `Examples in that documentation
<https://docs.python.org/3/library/asyncio-stream.html>`_
may be of assistance in writing production senders and
receivers.

HL7 Sender
----------

.. code:: python

    # Using the third party `aiorun` instead of the `asyncio.run()` to avoid
    # boilerplate.
    import aiorun

    import hl7
    from hl7.mllp import open_hl7_connection


    async def main():
        message = 'MSH|^~\&|GHH LAB|ELAB-3|GHH OE|BLDG4|200202150930||ORU^R01|CNTRL-3456|P|2.4\r'
        message += 'PID|||555-44-4444||EVERYWOMAN^EVE^E^^^^L|JONES|196203520|F|||153 FERNWOOD DR.^^STATESVILLE^OH^35292||(206)3345232|(206)752-121||||AC555444444||67-A4335^OH^20030520\r'
        message += 'OBR|1|845439^GHH OE|1045813^GHH LAB|1554-5^GLUCOSE|||200202150730||||||||555-55-5555^PRIMARY^PATRICIA P^^^^MD^^LEVEL SEVEN HEALTHCARE, INC.|||||||||F||||||444-44-4444^HIPPOCRATES^HOWARD H^^^^MD\r'
        message += 'OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F\r'

        # Open the connection to the HL7 receiver.
        # Using wait_for is optional, but recommended so
        # a dead receiver won't block you for long
        hl7_reader, hl7_writer = await asyncio.wait_for(
            open_hl7_connection("127.0.0.1", 2575),
            timeout=10,
        )

        hl7_message = hl7.parse(message)

        # Write the HL7 message, and then wait for the writer
        # to drain to actually send the message
        hl7_writer.writemessage(hl7_message)
        await hl7_writer.drain()
        print(f'Sent message\n {hl7_message}'.replace('\r', '\n'))

        # Now wait for the ACK message from the receiever
        hl7_ack = await asyncio.wait_for(
          hl7_reader.readmessage(),
          timeout=10
        )
        print(f'Received ACK\n {hl7_ack}'.replace('\r', '\n'))


    aiorun.run(main(), stop_on_unhandled_errors=True)

HL7 Receiver
------------

.. code:: python

    # Using the third party `aiorun` instead of the `asyncio.run()` to avoid
    # boilerplate.
    import aiorun

    import hl7
    from hl7.mllp import start_hl7_server


    async def process_hl7_messages(hl7_reader, hl7_writer):
        """This will be called every time a socket connects
        with us.
        """
        peername = hl7_writer.get_extra_info("peername")
        print(f"Connection established {peername}")
        try:
            # We're going to keep listening until the writer
            # is closed. Only writers have closed status.
            while not hl7_writer.is_closing():
                hl7_message = await hl7_reader.readmessage()
                print(f'Received message\n {hl7_message}'.replace('\r', '\n'))
                # Now let's send the ACK and wait for the
                # writer to drain
                hl7_writer.writemessage(hl7_message.create_ack())
                await hl7_writer.drain()
        except asyncio.IncompleteReadError:
            # Oops, something went wrong, if the writer is not
            # closed or closing, close it.
            if not hl7_writer.is_closing():
                hl7_writer.close()
                await hl7_writer.wait_closed()
        print(f"Connection closed {peername}")


    async def main():
        try:
            # Start the server in a with clause to make sure we
            # close it
            async with await start_hl7_server(
                process_hl7_messages, port=2575
            ) as hl7_server:
                # And now we server forever. Or until we are
                # cancelled...
                await hl7_server.serve_forever()
        except asyncio.CancelledError:
            # Cancelled errors are expected
            pass
        except Exception:
            print("Error occurred in main")


    aiorun.run(main(), stop_on_unhandled_errors=True)
