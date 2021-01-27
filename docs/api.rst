python-hl7 API
==============

.. testsetup:: *

   import hl7
   message = 'MSH|^~\&|GHH LAB|ELAB-3|GHH OE|BLDG4|200202150930||ORU^R01|CNTRL-3456|P|2.4\r'
   message += 'PID|||555-44-4444||EVERYWOMAN^EVE^E^^^^L|JONES|196203520|F|||153 FERNWOOD DR.^^STATESVILLE^OH^35292||(206)3345232|(206)752-121||||AC555444444||67-A4335^OH^20030520\r'
   message += 'OBR|1|845439^GHH OE|1045813^GHH LAB|1554-5^GLUCOSE|||200202150730||||||||555-55-5555^PRIMARY^PATRICIA P^^^^MD^^LEVEL SEVEN HEALTHCARE, INC.|||||||||F||||||444-44-4444^HIPPOCRATES^HOWARD H^^^^MD\r'
   message += 'OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F\r'

.. autodata:: hl7.NULL

.. autofunction:: hl7.parse

.. autofunction:: hl7.parse_batch

.. autofunction:: hl7.parse_file

.. autofunction:: hl7.parse_hl7

.. autofunction:: hl7.ishl7

.. autofunction:: hl7.isbatch

.. autofunction:: hl7.isfile

.. autofunction:: hl7.split_file

.. autofunction:: hl7.generate_message_control_id

.. autofunction:: hl7.parse_datetime


Data Types
----------

.. autoclass:: hl7.Sequence
   :members: __call__

.. autoclass:: hl7.Container
   :members: __str__

.. autoclass:: hl7.Accessor
   :members: __new__, parse_key, key, _replace, _make, _asdict, segment, segment_num, field_num, repeat_num, component_num, subcomponent_num

.. autoclass:: hl7.Batch
   :members: __str__, header, trailer, create_header, create_trailer, create_file, create_batch, create_message, create_segment, create_field, create_repetition, create_component

.. autoclass:: hl7.File
   :members: __str__, header, trailer, create_header, create_trailer, create_file, create_batch, create_message, create_segment, create_field, create_repetition, create_component

.. autoclass:: hl7.Message
   :members: segments, segment, __getitem__, __setitem__, __str__, escape, unescape, extract_field, assign_field, create_file, create_batch, create_message, create_segment, create_field, create_repetition, create_component, create_ack

.. autoclass:: hl7.Segment

.. autoclass:: hl7.Field

.. autoclass:: hl7.Repetition

.. autoclass:: hl7.Component

.. autoclass:: hl7.Factory
   :members:


MLLP Network Client
-------------------

.. autoclass:: hl7.client.MLLPClient
   :members: send_message, send, close

MLLP Asyncio
------------

.. autofunction:: hl7.mllp.open_hl7_connection

.. autofunction:: hl7.mllp.start_hl7_server

.. autoclass:: hl7.mllp.HL7StreamReader
   :members: readmessage

.. autoclass:: hl7.mllp.HL7StreamWriter
   :members: writemessage

.. autoclass:: hl7.mllp.InvalidBlockError
