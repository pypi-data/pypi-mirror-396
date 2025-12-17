from typing import Union
from datetime import datetime as dt, timedelta

from iolink_utils.definitions.timing import getMaxFrameTransmissionDelay_master, getMaxResponseTime, \
    getMaxFrameTransmissionDelay_device
from ._octetStreamDecoderInternal import DecodingState, MessageState, DeviceMessageDecoder, MasterMessageDecoder
from .octetStreamDecoderSettings import DecoderSettings
from .octetStreamDecoderMessages import DeviceMessage, MasterMessage


class OctetStreamDecoder:
    def __init__(self, settings: DecoderSettings):
        self.settings: DecoderSettings = settings

        self.state: DecodingState = DecodingState.Idle
        self.messageDecoder: Union[None, MasterMessageDecoder, DeviceMessageDecoder] = None
        self.lastMasterMessage: Union[None, MasterMessage] = None
        self.lastDeviceMessage: Union[None, DeviceMessage] = None

        self.lastProcessedOctetEndTime: dt = dt(1970, 1, 1)

        self.timingConstraints = {
            DecodingState.Idle: 0,
            DecodingState.MasterMessage: getMaxFrameTransmissionDelay_master(self.settings.transmissionRate),
            DecodingState.DeviceResponseDelay: getMaxResponseTime(self.settings.transmissionRate),
            DecodingState.DeviceMessage: getMaxFrameTransmissionDelay_device(self.settings.transmissionRate),
        }
        self.maxFrameTransmissionDelay: float = self.timingConstraints[DecodingState.Idle]

    def _updateTimingConstraint(self, state: DecodingState):
        self.maxFrameTransmissionDelay = self.timingConstraints[state]

    def _isWithinTimingConstraints(self, octetStartTime: dt) -> bool:
        return (octetStartTime - self.lastProcessedOctetEndTime) < timedelta(
            microseconds=self.maxFrameTransmissionDelay)

    def _gotoState(self, state: DecodingState):
        self.state = state
        self._updateTimingConstraint(self.state)

    def reset(self):
        self.state: DecodingState = DecodingState.Idle

    def processOctet(self, octet, start_time: dt, end_time: dt) -> Union[None, MasterMessage, DeviceMessage]:
        if self.state == DecodingState.Idle or not self._isWithinTimingConstraints(start_time):
            self.messageDecoder = MasterMessageDecoder(self.settings)
            self._gotoState(DecodingState.MasterMessage)
            self.lastMasterMessage = None
            self.lastDeviceMessage = None
        self.lastProcessedOctetEndTime = end_time

        if self.state == DecodingState.MasterMessage:
            if self.messageDecoder.processOctet(octet, start_time, end_time) == MessageState.Finished:
                self._gotoState(DecodingState.DeviceResponseDelay)
                self.lastMasterMessage = self.messageDecoder.msg
                return self.lastMasterMessage

        if self.state == DecodingState.DeviceResponseDelay:
            self.messageDecoder = DeviceMessageDecoder(self.settings, self.lastMasterMessage.mc.read,
                                                       self.lastMasterMessage.ckt.mSeqType)
            self._gotoState(DecodingState.DeviceMessage)

        if self.state == DecodingState.DeviceMessage:
            if self.messageDecoder.processOctet(octet, start_time, end_time) == MessageState.Finished:
                self._gotoState(DecodingState.Idle)
                self.lastDeviceMessage = self.messageDecoder.msg
                return self.lastDeviceMessage

        return None
