import abc
from enum import IntEnum
from datetime import datetime as dt

from iolink_utils.octetDecoder.octetDecoder import IService
from abc import ABC, abstractmethod


# See Table A.12 – Definition of the nibble "I-Service"
class IServiceNibble(IntEnum):
    NoService = 0b0000,
    M_WriteReq_8bitIdx = 0b0001,
    M_WriteReq_8bitIdxSub = 0b0010,
    M_WriteReq_16bitIdxSub = 0b0011,
    D_WriteResp_M = 0b0100,
    D_WriteResp_P = 0b0101,
    M_ReadReq_8bitIdx = 0b1001,
    M_ReadReq_8bitIdxSub = 0b1010,
    M_ReadReq_16bitIdxSub = 0b1011,
    D_ReadResp_M = 0b1100,
    D_ReadResp_P = 0b1101


class FlowCtrl:
    class State(IntEnum):
        Count = 0
        Start = 1
        Idle = 2
        Reserved = 3
        Abort = 4

    def __init__(self, value: int = 0x11):
        # See Table 52 – FlowCTRL definitions
        mappings = [
            (range(0x00, 0x10), FlowCtrl.State.Count),  # 0x00–0x0F
            ([0x10], FlowCtrl.State.Start),
            ([0x11, 0x12], FlowCtrl.State.Idle),
            (range(0x13, 0x1F), FlowCtrl.State.Reserved),  # 0x13–0x1E
            ([0x1F], FlowCtrl.State.Abort),
        ]

        for key_range, state in mappings:
            if value in key_range:
                self.state = state
                self.value = value
                return

        raise ValueError(f"Invalid FlowCtrl value: {value}")


class ISDU(ABC):
    def __init__(self, iService: IService):
        self.flowCtrl: FlowCtrl = FlowCtrl()

        self.service = IServiceNibble(iService.service)
        self.length = iService.length
        self.rawData: bytearray = bytearray()
        self.chkpdu: int = 0

        self.isValid = False
        self.isComplete = False

        self.start_time = dt(1970, 1, 1)
        self.end_time = dt(1970, 1, 1)

    def _hasExtendedLength(self):
        return self.length == 1

    def _getTotalLength(self):
        return int(self.rawData[1]) if self._hasExtendedLength() else self.length

    def _calculateCheckByte(self) -> int:
        chk = 0
        for b in self.rawData[:-1]:  # except chkpdu which is last byte
            chk ^= b
        return chk

    def setStartTime(self, start_time: dt):
        self.start_time = start_time

    def setEndTime(self, end_time: dt):
        self.end_time = end_time

    def appendOctets(self, flowCtrl: FlowCtrl, requestData: bytearray) -> bool:
        if flowCtrl.state == FlowCtrl.State.Start or flowCtrl.state == FlowCtrl.State.Count:
            # TODO if same count value, replace last received data
            self.rawData.extend(requestData)

            targetLength = self._getTotalLength()
            if len(self.rawData) > targetLength:
                self.rawData = self.rawData[:targetLength]
        self.flowCtrl = flowCtrl

        if len(self.rawData) == self._getTotalLength():
            self.chkpdu = self.rawData[-1]
            self.isValid = self.chkpdu == self._calculateCheckByte()
            self.isComplete = True
        return self.isComplete

    @abstractmethod
    def name(self) -> str:  # pragma: no cover
        return 'ISDU'

    @abstractmethod
    def data(self) -> dict:  # pragma: no cover
        return {}
