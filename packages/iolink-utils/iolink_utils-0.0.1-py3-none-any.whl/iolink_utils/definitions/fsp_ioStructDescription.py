from dataclasses import dataclass, field
from typing import List
from iolink_utils.crc.crc import crc16


@dataclass
class FSP_IOStructDescription:
    """
    See IOL SafetySpec: Table A.4 – Generic FS I/O data structure description
    """

    @dataclass
    class Description:
        DataRange: int = 0
        TotalOfBits: int = 0
        TotalOfOctets: int = 0
        TotalOfInt16: int = 0
        TotalOfInt32: int = 0

    IO_DescVersion: int = 0x01
    input: Description = field(default_factory=Description)
    output: Description = field(default_factory=Description)

    def calculateFSPIOStructCRC(self) -> int:
        fields: List[int] = [
            self.IO_DescVersion,
            self.input.DataRange,
            self.input.TotalOfBits,
            self.input.TotalOfOctets,
            self.input.TotalOfInt16,
            self.input.TotalOfInt32,
            self.output.DataRange,
            self.output.TotalOfBits,
            self.output.TotalOfOctets,
            self.output.TotalOfInt16,
            self.output.TotalOfInt32
        ]

        return crc16(bytearray(fields))
