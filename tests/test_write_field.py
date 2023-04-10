from unittest import TestCase

import hl7

sample_hl7_1 = "\r".join(
    [
        "MSH|^~\\&|field|rep1~rep2|comp1^comp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r",
    ]
)



class WriteFieldTest(TestCase):
    """Test the write_field() function, which escapes the value to be written."""
    def test_escape_separators(self):
        """Test writing a field with separators in it"""

        msg = hl7.parse(sample_hl7_1)
        seg = msg[0]

        # Write to field via the Segment object with escaping.
        seg.write_field("New with Field | rep ~ sub & and escape \\", 4)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|field|New with Field \\F\\ rep \\R\\ sub \\T\\ and escape \\E\\|comp1^comp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")

        # Write to field via the Message object with escaping.
        msg.write_field("New with Field | rep ~ sub & and escape \\", "MSH", 1, 5, 1, 1)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|field|New with Field \\F\\ rep \\R\\ sub \\T\\ and escape \\E\\|New with Field \\F\\ rep \\R\\ sub \\T\\ and escape \\E\\^comp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")