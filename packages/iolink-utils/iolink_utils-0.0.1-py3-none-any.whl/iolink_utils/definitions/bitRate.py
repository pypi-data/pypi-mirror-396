from enum import IntEnum
from ._internal import AutoNameConvertMeta


# See Table 9 – Dynamic characteristics of the transmission
class BitRate(IntEnum, metaclass=AutoNameConvertMeta):
    Undefined = 0
    COM1 = 4800
    COM2 = 38400
    COM3 = 230400
