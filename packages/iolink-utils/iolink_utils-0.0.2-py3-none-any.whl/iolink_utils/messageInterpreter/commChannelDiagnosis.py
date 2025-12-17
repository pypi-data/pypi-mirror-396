from typing import Dict
from datetime import datetime as dt
from enum import IntEnum

from iolink_utils.octetDecoder.octetStreamDecoderMessages import DeviceMessage, MasterMessage
from iolink_utils.definitions.transmissionDirection import TransmissionDirection
from iolink_utils.octetDecoder.octetDecoder import (StatusCodeType1, StatusCodeType2, Event)
from iolink_utils.definitions.events import EventType, EventMode


class TransactionDiagEventMemory:
    def __init__(self, start_time: dt, end_time: dt, eventMemory: bytearray):
        self.start_time: dt = start_time
        self.end_time: dt = end_time

        self.eventMemory: bytearray = eventMemory

    def _getStatusCode(self):
        if not self.eventMemory:
            return "no data"

        statusCode = StatusCodeType2.from_buffer_copy(self.eventMemory, 0)
        if statusCode.details == 0:  # legacy
            statusCode = StatusCodeType1.from_buffer_copy(self.eventMemory, 0)

        return str(statusCode)

    def _getEvents(self):
        events = []

        statusCode = StatusCodeType2.from_buffer_copy(self.eventMemory, 0)
        if statusCode.details == 1:
            event_offsets = [1 + 3 * i for i in range(6)]
            event_flags = [
                statusCode.evt1,
                statusCode.evt2,
                statusCode.evt3,
                statusCode.evt4,
                statusCode.evt5,
                statusCode.evt6,
            ]

            for idx, (flag, offset) in enumerate(zip(event_flags, event_offsets), start=1):
                if flag:
                    evt = Event.from_buffer_copy(self.eventMemory, offset)
                    events.append((idx,
                                   f"{EventType(evt.qualifier.type).name}{EventMode(evt.qualifier.mode).name}({evt.code.code})"))

        return events

    def data(self) -> Dict:
        return {
            'evtStatus': self._getStatusCode(),
            **{f'evt{idx}': info for idx, info in self._getEvents()}
        }

    def __str__(self):
        return f"Diag EventMem: '{self.data()}"


class TransactionDiagEventReset:
    def __init__(self, start_time: dt, end_time: dt):
        self.start_time: dt = start_time
        self.end_time: dt = end_time

    def data(self) -> Dict:
        return {}

    def __str__(self):
        return f"Diag Reset"


class CommChannelDiagnosis:
    class State(IntEnum):
        Idle = 0,
        ReadEventMemory = 1,
        ResetEventFlag = 2

    def __init__(self):
        self.state: CommChannelDiagnosis.State = CommChannelDiagnosis.State.Idle

        self.read_startTime: dt = dt(1970, 1, 1)
        self.read_endTime: dt = dt(1970, 1, 1)

        self.reset_startTime: dt = dt(1970, 1, 1)
        self.reset_endTime: dt = dt(1970, 1, 1)

        self.direction: TransmissionDirection = TransmissionDirection.Read
        self.eventMemory: bytearray = bytearray()
        self.eventMemoryIndex: int = 0

    def processMasterMessage(self, message: MasterMessage):
        self.direction = TransmissionDirection(message.mc.read)
        self.eventMemoryIndex = message.mc.address

        if self.state == CommChannelDiagnosis.State.Idle:
            self.eventMemory = bytearray()

            if self.direction == TransmissionDirection.Write and self.eventMemoryIndex == 0:
                self.reset_startTime = message.start_time
                self.state = CommChannelDiagnosis.State.ResetEventFlag
            elif self.direction == TransmissionDirection.Read:
                self.read_startTime = message.start_time
                self.state = CommChannelDiagnosis.State.ReadEventMemory

        elif self.state == CommChannelDiagnosis.State.ReadEventMemory:
            if self.direction == TransmissionDirection.Write and self.eventMemoryIndex == 0:
                self.reset_startTime = message.start_time
                self.state = CommChannelDiagnosis.State.ResetEventFlag

        return []

    def processDeviceMessage(self, message: DeviceMessage):
        transactions = []

        if self.state == CommChannelDiagnosis.State.ReadEventMemory:
            self.read_endTime = message.end_time
            if self.eventMemoryIndex == len(self.eventMemory):
                self.eventMemory.append(message.od[0])
            else:  # something is wrong TODO reset received data / error handling
                self.state = CommChannelDiagnosis.State.Idle
        elif self.state == CommChannelDiagnosis.State.ResetEventFlag:
            self.reset_endTime = message.end_time
            transactions.append(TransactionDiagEventMemory(self.read_startTime, self.read_endTime, self.eventMemory))
            transactions.append(TransactionDiagEventReset(self.reset_startTime, self.reset_endTime))
            self.state = CommChannelDiagnosis.State.Idle

        return transactions
