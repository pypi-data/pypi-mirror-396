from iolink_utils.octetDecoder.octetDecoder import IService
from iolink_utils.messageInterpreter.ISDU import IServiceNibble, FlowCtrl, ISDU


class ISDURequest_Write8bitIdx(ISDU):
    def __init__(self, iService: IService):
        super().__init__(iService)
        self.index: int = 0

    def appendOctets(self, flowCtrl: FlowCtrl, requestData: bytearray) -> bool:
        finished = super().appendOctets(flowCtrl, requestData)

        if finished:
            pos = 2 if self._hasExtendedLength() else 1
            self.index = int(self.rawData[pos])
        return finished

    def name(self) -> str:
        return 'Write8bitIdx'

    def data(self) -> dict:
        return {
            'valid': self.isValid,
            'index': self.index,
            'data': self.rawData  # TODO payload only
        }

    def __str__(self):  # pragma: no cover
        return f"ISDURequest_Write8bitIdx(index={self.index} data={self.rawData.hex()})"


class ISDURequest_Write8bitIdxSub(ISDU):
    def __init__(self, iService: IService):
        super().__init__(iService)
        self.index: int = 0
        self.subIndex: int = 0

    def appendOctets(self, flowCtrl: FlowCtrl, requestData: bytearray) -> bool:
        finished = super().appendOctets(flowCtrl, requestData)

        if finished:
            pos = 2 if self._hasExtendedLength() else 1
            self.index = int(self.rawData[pos])
            self.subIndex = int(self.rawData[pos + 1])
        return finished

    def name(self) -> str:
        return 'Write8bitIdxSub'

    def data(self) -> dict:
        return {
            'valid': self.isValid,
            'index': self.index,
            'subIndex': self.subIndex,
            'data': self.rawData  # TODO payload only
        }

    def __str__(self):  # pragma: no cover
        return f"ISDURequest_Write8bitIdxSub(index={self.index} subIndex={self.subIndex} data={self.rawData.hex()})"


class ISDURequest_Write16bitIdxSub(ISDU):
    def __init__(self, iService: IService):
        super().__init__(iService)
        self.index: int = 0
        self.subIndex: int = 0

    def appendOctets(self, flowCtrl: FlowCtrl, requestData: bytearray) -> bool:
        finished = super().appendOctets(flowCtrl, requestData)

        if finished:
            pos = 2 if self._hasExtendedLength() else 1
            self.index = int.from_bytes(self.rawData[pos:pos + 2], byteorder='big')
            self.subIndex = int(self.rawData[pos + 2])
        return finished

    def name(self) -> str:
        return 'Write16bitIdxSub'

    def data(self) -> dict:
        return {
            'valid': self.isValid,
            'index': self.index,
            'subIndex': self.subIndex,
            'data': self.rawData  # TODO payload only
        }

    def __str__(self):  # pragma: no cover
        return f"ISDURequest_Write16bitIdxSub(index={self.index} subIndex={self.subIndex} data={self.rawData.hex()})"


### READ ###

class ISDURequest_Read8bitIdx(ISDU):
    def __init__(self, iService: IService):
        super().__init__(iService)
        self.index: int = 0

    def appendOctets(self, flowCtrl: FlowCtrl, requestData: bytearray) -> bool:
        finished = super().appendOctets(flowCtrl, requestData)

        if finished:
            self.index = int(self.rawData[1])
        return finished

    def name(self) -> str:
        return 'Read8bitIdx'

    def data(self) -> dict:
        return {
            'valid': self.isValid,
            'index': self.index
        }

    def __str__(self):  # pragma: no cover
        return f"ISDURequest_Read8bitIdx(index={self.index} data={self.rawData.hex()})"


class ISDURequest_Read8bitIdxSub(ISDU):
    def __init__(self, iService: IService):
        super().__init__(iService)
        self.index: int = 0
        self.subIndex: int = 0

    def appendOctets(self, flowCtrl: FlowCtrl, requestData: bytearray) -> bool:
        finished = super().appendOctets(flowCtrl, requestData)

        if finished:
            self.index = int(self.rawData[1])
            self.subIndex = int(self.rawData[2])
        return finished

    def name(self) -> str:
        return 'Read8bitIdxSub'

    def data(self) -> dict:
        return {
            'valid': self.isValid,
            'index': self.index,
            'subIndex': self.subIndex
        }

    def __str__(self):  # pragma: no cover
        return f"ISDURequest_Read8bitIdxSub(index={self.index} subIndex={self.subIndex} data={self.rawData.hex()})"


class ISDURequest_Read16bitIdxSub(ISDU):
    def __init__(self, iService: IService):
        super().__init__(iService)
        self.index: int = 0
        self.subIndex: int = 0

    def appendOctets(self, flowCtrl: FlowCtrl, requestData: bytearray) -> bool:
        finished = super().appendOctets(flowCtrl, requestData)

        if finished:
            self.index = int.from_bytes(self.rawData[1:2], byteorder='big')
            self.subIndex = int(self.rawData[3])
        return finished

    def name(self) -> str:
        return 'Read16bitIdxSub'

    def data(self) -> dict:
        return {
            'name': 'Read16bitIdxSub',
            'valid': self.isValid,
            'index': self.index,
            'subIndex': self.subIndex
        }

    def __str__(self):  # pragma: no cover
        return f"ISDURequest_Read16bitIdxSub(index={self.index} subIndex={self.subIndex} data={self.rawData.hex()})"


def createISDURequest(iService: IService):
    _req_map = {
        IServiceNibble.M_WriteReq_8bitIdx: ISDURequest_Write8bitIdx,
        IServiceNibble.M_WriteReq_8bitIdxSub: ISDURequest_Write8bitIdxSub,
        IServiceNibble.M_WriteReq_16bitIdxSub: ISDURequest_Write16bitIdxSub,
        IServiceNibble.M_ReadReq_8bitIdx: ISDURequest_Read8bitIdx,
        IServiceNibble.M_ReadReq_8bitIdxSub: ISDURequest_Read8bitIdxSub,
        IServiceNibble.M_ReadReq_16bitIdxSub: ISDURequest_Read16bitIdxSub,
    }

    if iService.service not in _req_map:
        raise ValueError(f"Invalid request nibble: {iService}")

    return _req_map[iService.service](iService)
