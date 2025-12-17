from typing import Optional
from iolink_utils.definitions.bitRate import BitRate
from iolink_utils.octetDecoder.octetDecoder import MSequenceCapability


class PhysicalLayer:
    def __init__(self):
        self.bitrate: BitRate = BitRate.Undefined
        self.min_cycle_time = 0
        self.sio_supported = False
        self.m_sequence_capability: Optional[MSequenceCapability] = None

    def __str__(self):  # pragma: no cover
        return (
            f"PhysicalLayer("
            f"bitrate={self.bitrate.name} ({self.bitrate.value}), "
            f"min_cycle_time={self.min_cycle_time}, "
            f"sio_supported={self.sio_supported}, "
            f"m_sequence_capability={self.m_sequence_capability})"
        )
