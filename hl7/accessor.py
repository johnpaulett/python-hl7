# -*- coding: utf-8 -*-
from collections import namedtuple


class Accessor(
    namedtuple(
        "Accessor",
        [
            "segment",
            "segment_num",
            "field_num",
            "repeat_num",
            "component_num",
            "subcomponent_num",
        ],
    )
):
    __slots__ = ()

    WILDCARD = object()

    def __new__(
        cls,
        segment,
        segment_num=1,
        field_num=None,
        repeat_num=None,
        component_num=None,
        subcomponent_num=None,
    ):
        """Create a new instance of Accessor for *segment*. Index numbers start from 1."""
        if (
            field_num is cls.WILDCARD
            or component_num is cls.WILDCARD
            or subcomponent_num is cls.WILDCARD
        ):
            raise ValueError("wildcard only supported for segment and repeat")
        return super(Accessor, cls).__new__(
            cls,
            segment,
            segment_num,
            field_num,
            repeat_num,
            component_num,
            subcomponent_num,
        )

    @property
    def key(self):
        """Return the string accessor key that represents this instance"""
        seg = (
            self.segment
            if self.segment_num == 1
            else self.segment
            + str("*" if self.segment_num is self.WILDCARD else self.segment_num)
        )
        return ".".join(
            str(f)
            for f in [
                seg,
                self.field_num,
                "*" if self.repeat_num is self.WILDCARD else self.repeat_num,
                self.component_num,
                self.subcomponent_num,
            ]
            if f is not None
        )

    def __str__(self):
        return self.key

    @classmethod
    def parse_key(cls, key):
        """Create an Accessor by parsing an accessor key.

        The key is defined as:

            |   SEG[n]-Fn-Rn-Cn-Sn
            |       F   Field
            |       R   Repeat
            |       C   Component
            |       S   Sub-Component
            |
            |   *Indexing is from 1 for compatibility with HL7 spec numbering.*
            |   'n' may be the wildcard specifier '*' for SEG[n] and Rn

        Example:

            |   PID.F1.R1.C2.S2 or PID.1.1.2.2
            |
            |   PID (default to first PID segment, counting from 1)
            |   F1  (first after segment id, HL7 Spec numbering)
            |   R1  (repeat counting from 1)
            |   C2  (component 2 counting from 1)
            |   S2  (component 2 counting from 1)
            |
            |   PID.1.*.2.2
            |
            |   return a list of sub-components, one for each repetition
        """

        def parse_part(keyparts, index, prefix, allow_wildcard=False):
            if len(keyparts) > index:
                num = keyparts[index]
                if num[0].upper() == prefix:
                    num = num[1:]
                if num == "*":
                    if allow_wildcard:
                        return Accessor.WILDCARD
                    else:
                        raise ValueError(f"wildcard not supported for {prefix}")
                else:
                    return int(num)
            else:
                return None

        parts = key.split(".")
        segment = parts[0][:3]
        if len(parts[0]) > 3:
            snum = parts[0][3:]
            segment_num = Accessor.WILDCARD if snum == "*" else int(snum)
        else:
            segment_num = 1
        field_num = parse_part(parts, 1, "F")
        repeat_num = parse_part(parts, 2, "R", allow_wildcard=True)
        component_num = parse_part(parts, 3, "C")
        subcomponent_num = parse_part(parts, 4, "S")
        return cls(
            segment, segment_num, field_num, repeat_num, component_num, subcomponent_num
        )
