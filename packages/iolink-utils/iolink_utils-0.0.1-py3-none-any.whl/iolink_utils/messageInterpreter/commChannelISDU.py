from typing import Dict
from datetime import datetime as dt
from enum import IntEnum

from iolink_utils.octetDecoder.octetStreamDecoderMessages import DeviceMessage, MasterMessage
from iolink_utils.octetDecoder.octetDecoder import IService
from iolink_utils.definitions.transmissionDirection import TransmissionDirection
from .ISDU import IServiceNibble, FlowCtrl
from .ISDUrequests import createISDURequest
from .ISDUresponses import createISDUResponse


class CommChannelISDU:
    class State(IntEnum):
        Idle = 0,
        Request = 1,
        RequestFinished = 2,
        WaitForResponse = 3,
        Response = 4,
        ResponseFinished = 5

    def __init__(self):
        self.state: CommChannelISDU.State = CommChannelISDU.State.Idle

        self.direction: TransmissionDirection = TransmissionDirection.Read
        self.flowCtrl: FlowCtrl = FlowCtrl()

        self.isduRequest = None
        self.isduResponse = None

        self.responseStartTime = None

    def processMasterMessage(self, message: MasterMessage):
        self.direction = TransmissionDirection(message.mc.read)
        self.flowCtrl = FlowCtrl(message.mc.address)

        if self.state == CommChannelISDU.State.Idle:
            if self.flowCtrl.state == FlowCtrl.State.Start and self.direction == TransmissionDirection.Write:
                self.isduRequest = createISDURequest(IService(message.od[0]))

                self.isduRequest.setStartTime(message.start_time)
                self.isduRequest.setEndTime(message.end_time)
                self.isduRequest.appendOctets(self.flowCtrl, message.od)

                if self.isduRequest.isComplete:
                    self.state = CommChannelISDU.State.RequestFinished
                else:
                    self.state = CommChannelISDU.State.Request

        elif self.state == CommChannelISDU.State.Request:
            if self.flowCtrl.state == FlowCtrl.State.Count:
                self.isduRequest.setEndTime(message.end_time)
                self.isduRequest.appendOctets(self.flowCtrl, message.od)

                if self.isduRequest.isComplete:
                    self.state = CommChannelISDU.State.RequestFinished

            elif self.flowCtrl.state == FlowCtrl.State.Abort:
                self.state = CommChannelISDU.State.Idle

        elif self.state == CommChannelISDU.State.WaitForResponse:
            if self.flowCtrl.state == FlowCtrl.State.Start and self.direction == TransmissionDirection.Read:
                self.responseStartTime = message.start_time

        return []

    def processDeviceMessage(self, message: DeviceMessage):
        isduTransactions = []

        if self.state == CommChannelISDU.State.RequestFinished:
            self.isduRequest.setEndTime(message.end_time)

            isduTransactions.append(self.isduRequest)
            self.state = CommChannelISDU.State.WaitForResponse

        elif self.state == CommChannelISDU.State.WaitForResponse:
            if self.flowCtrl.state == FlowCtrl.State.Start:
                if IService(message.od[0]).service != IServiceNibble.NoService:
                    self.isduResponse = createISDUResponse(IService(message.od[0]))

                    self.isduResponse.setStartTime(self.responseStartTime)
                    self.isduResponse.setEndTime(message.end_time)
                    self.isduResponse.appendOctets(self.flowCtrl, message.od)

                    if self.isduResponse.isComplete:
                        isduTransactions.append(self.isduResponse)
                        self.state = CommChannelISDU.State.Idle
                    else:
                        self.state = CommChannelISDU.State.Response

        elif self.state == CommChannelISDU.State.Response:
            if self.flowCtrl.state == FlowCtrl.State.Count:
                self.isduResponse.setEndTime(message.end_time)
                self.isduResponse.appendOctets(self.flowCtrl, message.od)

                if self.isduResponse.isComplete:
                    isduTransactions.append(self.isduResponse)
                    self.state = CommChannelISDU.State.Idle

            elif self.flowCtrl.state == FlowCtrl.State.Abort:
                self.state = CommChannelISDU.State.Idle

        return isduTransactions
