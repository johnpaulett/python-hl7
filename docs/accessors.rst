Message Accessor
================

Reproduced from: http://wiki.medical-objects.com.au/index.php/Hl7v2_parsing

.. note::

   Warning: Indexes in this API are from 1, not 0. This is to align with the HL7 documentation.

Example HL7 Fragment:

.. doctest::

    >>> message = 'MSH|^~\&|\r'
    >>> message += 'PID|Field1|Component1^Component2|Component1^Sub-Component1&Sub-Component2^Component3|Repeat1~Repeat2\r\r'

    >>> import hl7
    >>> h = hl7.parse(message)

The resulting parse tree with values in quotes:

 |  Segment = "PID"
 |      F1
 |          R1 = "Field1"
 |      F2
 |          R1
 |              C1 = "Component1"
 |              C2 = "Component2"
 |      F3
 |          R1
 |              C1 = "Component1"
 |              C2
 |                  S1 = "Sub-Component1"
 |                  S2 = "Sub-Component2"
 |              C3 = "Component3"
 |      F4
 |          R1 = "Repeat1"
 |          R2 = "Repeat2"

 |  Legend
 |
 |      F   Field
 |      R   Repeat
 |      C   Component
 |      S   Sub-Component

A tree has leaf values and nodes. Only the leaves of the tree can have a value.
All data items in the message will be in a leaf node.

After parsing, the data items in the message are in position in the parse tree, but
they remain in their escaped form. To extract a value from the tree you start at the
root of the Segment and specify the details of which field value you want to extract.
The minimum specification is the field number and repeat number. If you are after a
component or sub-component value you also have to specify these values.

If for instance if you want to read the value "Sub-Component2" from the example HL7
you need to specify: Field 3, Repeat 1, Component 2, Sub-Component 2 (PID.F1.R1.C2.S2).
Reading values from a tree structure in this manner is the only safe way to read data
from a message.

.. doctest::

    >>> h['PID.F1.R1']
    'Field1'

    >>> h['PID.F2.R1.C1']
    'Component1'

You can also access values using :py:class:`hl7.Accessor`, or by directly calling
:py:meth:`hl7.Message.extract_field`. The following are all equivalent:

.. doctest::

    >>> h['PID.F2.R1.C1']
    'Component1'

    >>> h[hl7.Accessor('PID', 1, 2, 1, 1)]
    'Component1'

    >>> h.extract_field('PID', 1, 2, 1, 1)
    'Component1'

All values should be accessed in this manner. Even if a field is marked as being
non-repeating a repeat of "1" should be specified as later version messages
could have a repeating value.

To enable backward and forward compatibility there are rules for reading values when the
tree does not match the specification (eg PID.F1.R1.C2.S2) The common example of this is
expanding a HL7 "IS" Value into a Codeded Value ("CE"). Systems reading a "IS" value would
read the Identifier field of a message with a "CE" value and systems expecting a "CE" value
would see a Coded Value with only the identifier specified. A common Australian example of
this is the OBX Units field, which was an "IS" value previously and became a "CE" Value
in later versions.

    |    Old Version: "\|mmol/l\|"      New Version: "\|mmol/l^^ISO+\|"

Systems expecting a simple "IS" value would read "OBX.F6.R1" and this would yield a value
in the tree for an old message but with a message with a Coded Value that tree node would
not have a value, but would have 3 child Components with the "mmol/l" value in the first
subcomponent. To resolve this issue where the tree is deeper than the specified path the
first node of every child node is traversed until a leaf node is found and that value is
returned.

.. doctest::

    >>> h['PID.F3.R1.C2']
    'Sub-Component1'

This is a general rule for reading values: **If the parse tree is deeper than the specified 
path continue following the first child branch until a leaf of the tree is encountered
and return that value (which could be blank).**

Systems expecting a Coded Value ("CE"), but reading a message with a simple "IS" value in it
have the opposite problem. They have a deeper specification but have reached a leaf node and
cannot follow the path any further. Reading a "CE" value requires multiple reads for each
sub-component but for the "Identifier" in this example the specification would be "OBX.F6.R1.C1".
The tree would stop at R1 so C1 would not exist. In this case the unsatisfied path elements
(C1 in this case) can be examined and if every one is position 1 then they can be ignored and
the leaf of the tree that was reached returned. If any of the unsatisfied paths are not in
position 1 then this cannot be done and the result is a blank string.

This is the second Rule for reading values: **If the parse tree terminates before the full path
is satisfied check each of the subsequent paths and if every one is specified at position 1
then the leaf value reached can be returned as the result.**

.. doctest::

    >>> h['PID.F1.R1.C1.S1']
    'Field1'

This is a general rule for reading values: **If the parse tree is deeper than the specified 
path continue following the first child branch until a leaf of the tree is encountered
and return that value (which could be blank).**

In the second example every value that makes up the Coded Value, other than the identifier
has a component position greater than one and when reading a message with a simple "IS"
value in it, every value other than the identifier would return a blank string.

Following these rules will result in excellent backward and forward compatibility. It is
important to allow the reading of values that do not exist in the parse tree by simply
returning a blank string. The two rules detailed above, along with the full tree specification
for all values being read from a message will eliminate many of the errors seen when
handling earlier and later message versions.

.. doctest::

    >>> h['PID.F10.R1']
    ''


At this point the desired value has either been located, or is absent, in which case a blank
string is returned.

Assignments
-----------

The accessors also support item assignments. However, the Message object must exist and the
separators must be validly assigned.

Create a response message.

.. doctest::

    >>> SEP = '|^~\&'
    >>> CR_SEP = '\r'
    >>> MSH = hl7.Segment(SEP[0], [hl7.Field(SEP[2], ['MSH'])])
    >>> MSA = hl7.Segment(SEP[0], [hl7.Field(SEP[2], ['MSA'])])
    >>> response = hl7.Message(CR_SEP, [MSH, MSA])
    >>> response['MSH.F1.R1'] = SEP[0]
    >>> response['MSH.F2.R1'] = SEP[1:]

    >>> str(response)
    'MSH|^~\\&|\rMSA\r'

Assign values into the message. You can only assign a string into the message (i.e. a leaf
of the tree).

.. doctest::

    >>> response['MSH.F9.R1.C1'] = 'ORU'
    >>> response['MSH.F9.R1.C2'] = 'R01'
    >>> response['MSH.F9.R1.C3'] = ''
    >>> response['MSH.F12.R1'] = '2.4'
    >>> response['MSA.F1.R1'] = 'AA'
    >>> response['MSA.F3.R1'] = 'Application Message'

    >>> str(response)
    'MSH|^~\\&|||||||ORU^R01^|||2.4\rMSA|AA||Application Message\r'

You can also assign values using :py:class:`hl7.Accessor`, or by directly calling
:py:meth:`hl7.Message.assign_field`. The following are all equivalent:

.. doctest::

    >>> response['MSA.F1.R1'] = 'AA'
    >>> response[hl7.Accessor('MSA', 1, 1, 1)] = 'AA'
    >>> response.assign_field('AA', 'MSA', 1, 1, 1)

Escaping Content
----------------

HL7 messages are transported using the 7bit ascii character set. Only characters between 
ascii 32 and 127 are used. Characters which cannot be transported using this range
of values must be 'escaped', that is replaced by a sequence of characters for transmission.

The stores values internally in the escaped format.  When the message is composed using
'str', the escaped value must be returned.

.. doctest::

    >>> message = 'MSH|^~\&|\r'
    >>> message += 'PID|Field1|\F\|\r\r'
    >>> h = hl7.parse(message)

    >>> str(h['PID'][0][2])
    '\\F\\'

    >>> h.unescape(str(h['PID'][0][2]))
    '|'

When the accessor is used to reference the field, the field is automatically unescaped.

.. doctest::

    >>> h['PID.F2.R1']
    '|'

The escape/unescape mechanism support replacing separator characters with their escaped
version and replacing non-ascii characters with hexadecimal versions.

The escape method returns a 'str' object. The unescape method returns a str object.

.. doctest::

    >>> h.unescape('\\F\\')
    '|'

    >>> h.unescape('\\R\\')
    '~'

    >>> h.unescape('\\S\\')
    '^'

    >>> h.unescape('\\T\\')
    '&'

    >>> h.unescape('\\X202020\\')
    '   '

    >>> h.escape('|~^&')
    '\\F\\\\R\\\\S\\\\T\\'

    >>> h.escape('áéíóú')
    '\\Xe1\\\\Xe9\\\\Xed\\\\Xf3\\\\Xfa\\'

**Presentation Characters**

HL7 defines a protocol for encoding presentation characters, These include highlighting,
and rich text functionality. The API does not currently allow for easy access to the
escape/unescape logic. You must overwrite the message class escape and unescape methods,
after parsing the message.
