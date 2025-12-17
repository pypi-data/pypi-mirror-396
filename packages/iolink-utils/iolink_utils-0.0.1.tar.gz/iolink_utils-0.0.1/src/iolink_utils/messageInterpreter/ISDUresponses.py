from datetime import datetime as dt

from iolink_utils.octetDecoder.octetDecoder import IService
from iolink_utils.messageInterpreter.ISDU import IServiceNibble, FlowCtrl, ISDU


class ISDUResponse_WriteResp_M(ISDU):
    def __init__(self, iService: IService):
        super().__init__(iService)
        self.errorCode: int = 0
        self.additionalCode: int = 0

    def appendOctets(self, flowCtrl: FlowCtrl, requestData: bytearray) -> bool:
        finished = super().appendOctets(flowCtrl, requestData)

        if finished:
            self.errorCode = int(self.rawData[1])
            self.additionalCode = int(self.rawData[2])
        return finished

    def name(self) -> str:
        return 'WriteResp_M'

    def data(self) -> dict:
        return {
            'valid': self.isValid,
            'errorCode': self.errorCode,
            'additionalCode': self.additionalCode
        }

    def __str__(self):  # pragma: no cover
        return f"ISDUResponse_WriteResp_M(errorCode={self.errorCode} additionalCode={self.additionalCode} data={self.rawData.hex()})"


class ISDUResponse_WriteResp_P(ISDU):
    def __init__(self, iService: IService):
        super().__init__(iService)

    def appendOctets(self, flowCtrl: FlowCtrl, requestData: bytearray) -> bool:
        return super().appendOctets(flowCtrl, requestData)

    def name(self) -> str:
        return 'WriteResp_P'

    def data(self) -> dict:
        return {
            'valid': self.isValid
        }

    def __str__(self):  # pragma: no cover
        return f"ISDUResponse_WriteResp_P(data={self.rawData.hex()})"


class ISDUResponse_ReadResp_M(ISDU):
    def __init__(self, iService: IService):
        super().__init__(iService)
        self.errorCode: int = 0
        self.additionalCode: int = 0

    def appendOctets(self, flowCtrl: FlowCtrl, requestData: bytearray) -> bool:
        finished = super().appendOctets(flowCtrl, requestData)

        if finished:
            self.errorCode = int(self.rawData[1])
            self.additionalCode = int(self.rawData[2])
        return finished

    def name(self) -> str:
        return 'ReadResp_M'

    def data(self) -> dict:
        return {
            'valid': self.isValid,
            'errorCode': self.errorCode,
            'additionalCode': self.additionalCode
        }

    def __str__(self):  # pragma: no cover
        return f"ISDUResponse_ReadResp_M(errorCode={self.errorCode} additionalCode={self.additionalCode} data={self.rawData.hex()})"


class ISDUResponse_ReadResp_P(ISDU):
    def __init__(self, iService: IService):
        super().__init__(iService)

    def appendOctets(self, flowCtrl: FlowCtrl, requestData: bytearray) -> bool:
        return super().appendOctets(flowCtrl, requestData)

    def name(self) -> str:
        return 'ReadResp_P'

    def data(self) -> dict:
        return {
            'valid': self.isValid,
            'data': self.rawData  # TODO payload only
        }

    def __str__(self):  # pragma: no cover
        return f"ISDUResponse_ReadResp_P(data={self.rawData.hex()})"


def createISDUResponse(iService: IService):
    _req_map = {
        IServiceNibble.D_WriteResp_M: ISDUResponse_WriteResp_M,
        IServiceNibble.D_WriteResp_P: ISDUResponse_WriteResp_P,
        IServiceNibble.D_ReadResp_M: ISDUResponse_ReadResp_M,
        IServiceNibble.D_ReadResp_P: ISDUResponse_ReadResp_P,
    }

    if iService.service not in _req_map:
        raise ValueError(f"Invalid request nibble: {iService}")

    return _req_map[iService.service](iService)
