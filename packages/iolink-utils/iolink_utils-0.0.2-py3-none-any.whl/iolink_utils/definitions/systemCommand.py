from enum import IntEnum


# See Table B.9 – Coding of SystemCommand
class SystemCommand(IntEnum):
    ParamUploadStart = 0x01,
    ParamUploadEnd = 0x02,
    ParamDownloadStart = 0x03,
    ParamDownloadEnd = 0x04,
    ParamDownloadStore = 0x05,
    ParamBreak = 0x06,
    DeviceReset = 0x80,
    ApplicationReset = 0x81,
    RestoreFactorySettings = 0x82,
    BackToBox = 0x83
