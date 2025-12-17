from enum import IntEnum


# See Table B.1 – Direct Parameter page 1 and 2
class DirectParameterPage1Index(IntEnum):
    MasterCommand = 0,
    MasterCycleTime = 1,
    MinCycleTime = 2,
    MSequenceCapability = 3,
    RevisionID = 4,
    ProcessDataIn = 5,
    ProcessDataOut = 6,
    VendorID_MSB = 7,
    VendorID_LSB = 8,
    DeviceID_MSB = 9,
    DeviceID = 10,
    DeviceID_LSB = 11,
    FunctionID_MSB = 12,
    FunctionID_LSB = 13,
    Reserved = 14,
    SystemCommand = 15
