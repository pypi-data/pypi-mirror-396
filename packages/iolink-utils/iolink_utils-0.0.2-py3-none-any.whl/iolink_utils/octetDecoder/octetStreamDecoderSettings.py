from dataclasses import dataclass
from iolink_utils.definitions.bitRate import BitRate
from iolink_utils.iodd.iodd import Iodd


@dataclass(frozen=True)
class MSeqPayloadLength:
    pdOut: int = 0
    od: int = 0
    pdIn: int = 0


class DecoderSettings:
    def __init__(self):
        self.transmissionRate: BitRate = BitRate('Undefined')
        self.startup: MSeqPayloadLength = MSeqPayloadLength()
        self.preoperate: MSeqPayloadLength = MSeqPayloadLength()
        self.operate: MSeqPayloadLength = MSeqPayloadLength()

    def getPayloadLength(self, mSeqType: int) -> MSeqPayloadLength:
        if mSeqType == 0:
            return self.startup
        elif mSeqType == 1:
            return self.preoperate
        elif mSeqType == 2:
            return self.operate
        else:
            raise ValueError(f"Invalid M-Sequence type: '{mSeqType}'")

    @staticmethod
    def fromIODD(iodd: Iodd):
        settings: DecoderSettings = DecoderSettings()

        settings.transmissionRate = iodd.physicalLayer.bitrate
        settings.startup = MSeqPayloadLength(pdOut=0, od=1, pdIn=0)
        settings.preoperate = MSeqPayloadLength(pdOut=0,
                                                od=iodd.size_OnRequestData[0],
                                                pdIn=0)
        settings.operate = MSeqPayloadLength(pdOut=iodd.size_PDout,
                                             od=iodd.size_OnRequestData[1],
                                             pdIn=iodd.size_PDin)

        return settings
