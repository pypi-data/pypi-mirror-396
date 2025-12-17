from typing import Union, Optional, List

from iolink_utils.octetDecoder.octetStreamDecoderMessages import DeviceMessage, MasterMessage
from iolink_utils.definitions.communicationChannel import CommChannel
from .commChannelDiagnosis import CommChannelDiagnosis, TransactionDiagEventMemory, TransactionDiagEventReset
from .commChannelISDU import CommChannelISDU
from .ISDU import ISDU
from .commChannelPage import CommChannelPage, TransactionPage


class CommChannelProcess:
    def processMasterMessage(self, message: MasterMessage):  # pragma: no cover
        return []

    def processDeviceMessage(self, message: DeviceMessage):  # pragma: no cover
        return []


class MessageInterpreter:
    def __init__(self):
        self.channels = {
            CommChannel.Process: CommChannelProcess(),
            CommChannel.Page: CommChannelPage(),
            CommChannel.Diagnosis: CommChannelDiagnosis(),
            CommChannel.ISDU: CommChannelISDU()
        }
        self.activeChannel: Optional[CommChannel] = CommChannel.Process

    def processMessage(self, message: Union[None, MasterMessage, DeviceMessage]) -> List[
        Union[TransactionPage, TransactionDiagEventMemory, TransactionDiagEventReset, ISDU]]:

        if isinstance(message, MasterMessage):
            self.activeChannel = CommChannel(message.mc.channel)
            self.channels[self.activeChannel].processMasterMessage(message)
        elif isinstance(message, DeviceMessage):
            return self.channels[self.activeChannel].processDeviceMessage(message)

        return []
