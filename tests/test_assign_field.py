from unittest import TestCase

import hl7

sample_hl7_1 = "\r".join(
    [
        "MSH|^~\\&|field|rep1~rep2|comp1^comp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r",
    ]
)

sample_hl7_2 = "\r".join(
    [
        "MSH|^~\\&|f1r1c1s1&f1r1c1s2^f1r1c2s1&f1r1c2s2~f1r2c1s1&f1r2c1s2^f1r2c2s1&f1r2c2s\r"
    ]
)

SEP = r"|^~\&"
CR_SEP = "\r"


class AssignFieldTest(TestCase):
    def test_assign_field(self):
        msg = hl7.parse(sample_hl7_1)
        seg = msg[0]
        seg.assign_field("NewField", 3)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewField|rep1~rep2|comp1^comp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")

        seg.assign_field("NewField", 4)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewField|NewField|comp1^comp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")

        seg.assign_field("NewField", 5)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewField|NewField|NewField|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")

        seg.assign_field("NewField", 6)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewField|NewField|NewField|NewField\r")

        seg.assign_field("NewField", 7)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewField|NewField|NewField|NewField|NewField\r")


    def test_assign_repeat(self):
        msg = hl7.parse(sample_hl7_1)
        seg = msg[0]

        seg.assign_field("NewRep", 3, 1)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewRep|rep1~rep2|comp1^comp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")

        seg.assign_field("NewRep2", 3, 2)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewRep~NewRep2|rep1~rep2|comp1^comp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")

        seg.assign_field("NewRep", 4, 1)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewRep~NewRep2|NewRep~rep2|comp1^comp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")

        seg.assign_field("NewRep2", 4, 2)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewRep~NewRep2|NewRep~NewRep2|comp1^comp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")


        seg.assign_field("NewRep", 5, 1)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewRep~NewRep2|NewRep~NewRep2|NewRep|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")

        seg.assign_field("NewRep2", 5, 2)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewRep~NewRep2|NewRep~NewRep2|NewRep~NewRep2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")

    def test_assign_component(self):
        msg = hl7.parse(sample_hl7_1)
        seg = msg[0]

        seg.assign_field("NewComp", 3, 1, 1)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewComp|rep1~rep2|comp1^comp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")

        seg.assign_field("NewComp2", 3, 1, 2)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewComp^NewComp2|rep1~rep2|comp1^comp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")

        seg.assign_field("NewComp3", 3, 2, 2)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewComp^NewComp2~^NewComp3|rep1~rep2|comp1^comp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")

        seg.assign_field("NewComp", 4, 1, 1)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewComp^NewComp2~^NewComp3|NewComp~rep2|comp1^comp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")

        seg.assign_field("NewComp2", 4, 1, 2)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewComp^NewComp2~^NewComp3|NewComp^NewComp2~rep2|comp1^comp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")

        seg.assign_field("NewComp", 5, 1, 1)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewComp^NewComp2~^NewComp3|NewComp^NewComp2~rep2|NewComp^comp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")

        seg.assign_field("NewComp2", 5, 1, 2)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewComp^NewComp2~^NewComp3|NewComp^NewComp2~rep2|NewComp^NewComp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")


        seg.assign_field("NewComp2", 6, 1, 2)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewComp^NewComp2~^NewComp3|NewComp^NewComp2~rep2|NewComp^NewComp2|rep1comp1^NewComp2~rep2comp1^rep1comp2\r")


    def test_assign_subcomponent(self):
        msg = hl7.parse(sample_hl7_2)
        seg = msg[0]

        seg.assign_field("NewSub", 3, 1, 2, 2)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|f1r1c1s1&f1r1c1s2^f1r1c2s1&NewSub~f1r2c1s1&f1r2c1s2^f1r2c2s1&f1r2c2s\r")
    
        seg.assign_field("NewComp", 3, 2, 1)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|f1r1c1s1&f1r1c1s2^f1r1c2s1&NewSub~NewComp^f1r2c2s1&f1r2c2s\r")

        seg.assign_field("NewRep", 3, 2)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|f1r1c1s1&f1r1c1s2^f1r1c2s1&NewSub~NewRep\r")

        seg.assign_field("NewField", 3)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|NewField\r")

        for field in [3,4]:
            for rep in [1,2]:
                for comp in [1,2]:
                    for sub in [1,2]:
                        seg.assign_field(f"f{field}r{rep}c{comp}s{sub}", field, rep, comp, sub)
        new_msg = str(msg)
        self.assertEqual(new_msg, 'MSH|^~\\&|f3r1c1s1&f3r1c1s2^f3r1c2s1&f3r1c2s2~f3r2c1s1&f3r2c1s2^f3r2c2s1&f3r2c2s2|f4r1c1s1&f4r1c1s2^f4r1c2s1&f4r1c2s2~f4r2c1s1&f4r2c1s2^f4r2c2s1&f4r2c2s2\r')




class EscapeTest(TestCase):
    def test_escape_separators(self):
        """Test assigning a field with separators in it"""
        # 2/27/2023:  This is known to fail.  assign_field does not escape the incoming data.
        #  however, to re-code it to do so breaks some of the parsing code that expects to write
        #  the separators.  
        msg = hl7.parse(sample_hl7_1)
        seg = msg[0]

        seg.assign_field("New with Field | rep ~ sub & and escape \\", 4)
        new_msg = str(msg)
        self.assertEqual(new_msg, "MSH|^~\\&|New with Field \\F\\ rep \\R\\ sub \\T\\ and escape \\E\\|rep1~rep2|comp1^comp2|rep1comp1^rep1comp2~rep2comp1^rep1comp2\r")