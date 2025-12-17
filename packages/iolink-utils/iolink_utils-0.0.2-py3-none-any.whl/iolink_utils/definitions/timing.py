from iolink_utils.exceptions import InvalidBitRate, InvalidOctetCount
from .bitRate import BitRate


def getBitTimeInUs(transmissionRate: BitRate) -> float:
    bitTimesInMicroSeconds = {
        BitRate.COM1: 208.33,
        BitRate.COM2: 26.04,
        BitRate.COM3: 4.34
    }

    if transmissionRate not in bitTimesInMicroSeconds:
        raise InvalidBitRate(f"Invalid BitRate: {transmissionRate}")
    return bitTimesInMicroSeconds[transmissionRate]


def getMaxFrameTransmissionDelay_master(transmissionRate: BitRate) -> float:
    """
    See A.3.3 UART frame transmission delay of Master (ports)
    0 ≤ t1 ≤ 1 TBIT
    :param transmissionRate: IO-Link baud rate
    :return: max allowed gap between master octets (in microseconds)
    """
    return getBitTimeInUs(transmissionRate) * 1


def getMaxFrameTransmissionDelay_device(transmissionRate: BitRate) -> float:
    """
    See A.3.4 UART frame transmission delay of Devices
    0 ≤ t2 ≤ 3 TBIT
    :param transmissionRate: IO-Link baud rate
    :return: max allowed gap between device octets (in microseconds)
    """
    return getBitTimeInUs(transmissionRate) * 3


def getMaxResponseTime(transmissionRate: BitRate) -> float:
    """
    See A.3.5 Response time of Devices
    1 TBIT ≤ tA ≤ 10 TBIT
    :param transmissionRate: IO-Link baud rate
    :return: max allowed response time in microseconds
    """
    return getBitTimeInUs(transmissionRate) * 10


def getMaxMSequenceTime(transmissionRate: BitRate, octetCountMaster: int, octetCountDevice: int) -> float:
    """
    See A.3.6 M-sequence time
    t M-sequence = (m+n) * 11 * TBIT + tA + (m-1) * t1 + (n-1) * t2
    :param transmissionRate: IO-Link baud rate
    :param octetCountMaster: number of octets send by master
    :param octetCountDevice: number of octets send by device
    :return: max duration of M-sequence (master and device transmission time in microseconds)
    """
    if octetCountMaster < 2:
        raise InvalidOctetCount("Number of master octets is invalid (min expected: 2 octets)")
    if octetCountDevice < 1:
        raise InvalidOctetCount("Number of device octets is invalid (min expected: 1 octets)")

    return ((octetCountMaster + octetCountDevice) * 11 * getBitTimeInUs(transmissionRate) +
            getMaxResponseTime(transmissionRate) +
            (octetCountMaster - 1) * getMaxFrameTransmissionDelay_master(transmissionRate) +
            (octetCountDevice - 1) * getMaxFrameTransmissionDelay_device(transmissionRate))
