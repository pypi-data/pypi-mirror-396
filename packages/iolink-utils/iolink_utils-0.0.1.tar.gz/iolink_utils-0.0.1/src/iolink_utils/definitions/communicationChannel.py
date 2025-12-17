from enum import IntEnum


class CommChannel(IntEnum):
    Process    = 0,
    Page       = 1,
    Diagnosis  = 2,
    ISDU       = 3
