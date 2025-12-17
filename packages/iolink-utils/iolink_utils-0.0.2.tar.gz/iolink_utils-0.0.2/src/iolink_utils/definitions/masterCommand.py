from enum import IntEnum


# See Table B.2 – Types of MasterCommands
class MasterCommand(IntEnum):
    Fallback = 0x5A,
    MasterIdent = 0x95,
    DeviceIdent = 0x96,
    DeviceStartup = 0x97,
    ProcessDataOutputOperate = 0x98,
    DeviceOperate = 0x99,
    DevicePreoperate = 0x9A
