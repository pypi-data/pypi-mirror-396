from enum import IntEnum


# See Table A.17 – Values of INSTANCE
class EventInstance(IntEnum):
    Unknown = 0,
    Application = 4,
    System = 5


# See Table A.18 – Values of SOURCE
class EventSource(IntEnum):
    Device = 0,
    Master = 1


# See Table A.19 – Values of TYPE
class EventType(IntEnum):
    Reserved = 0,
    Notification = 1,
    Warning = 2,
    Error = 3


# See Table A.20 – Values of MODE
class EventMode(IntEnum):
    Reserved = 0,
    SingleShot = 1,
    Disappear = 2,
    Appear = 3
