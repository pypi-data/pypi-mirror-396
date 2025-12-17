from iolink_utils.exceptions import InvalidCycleTime, InvalidOctetValue
from iolink_utils.octetDecoder.octetDecoder import CycleTimeOctet
from math import ceil


class CycleTime:
    _PARAMS = {
        0: {"offset": 0.0, "base": 0.1, "range": (0.4, 6.3)},
        1: {"offset": 6.4, "base": 0.4, "range": (6.4, 31.6)},
        2: {"offset": 32.0, "base": 1.6, "range": (32.0, 132.8)},
    }

    @staticmethod
    def decodeToTimeInMs(octet: CycleTimeOctet) -> float:
        """Return the decoded time value in milliseconds."""
        params = CycleTime._PARAMS.get(octet.timeBaseCode)
        if not params:
            raise InvalidOctetValue(f"Invalid timeBaseCode: {octet.timeBaseCode}")
        return round(params["offset"] + params["base"] * octet.multiplier, 1)

    @staticmethod
    def encodeAsCycleTimeOctet(timeInMs: float) -> CycleTimeOctet:
        """Set the encoded time fields for the given millisecond value."""
        if timeInMs < 0:
            raise InvalidCycleTime("Time value must be non-negative")

        octet: CycleTimeOctet = CycleTimeOctet()
        if timeInMs == 0:
            octet.timeBaseCode = 0
            octet.multiplier = 0
            return octet

        for code, params in CycleTime._PARAMS.items():
            minTime, maxTime = params["range"]
            if minTime <= timeInMs <= maxTime:
                octet.timeBaseCode = code
                octet.multiplier = ceil(round((timeInMs - params["offset"]) / params["base"], 1))
                return octet

        raise InvalidCycleTime(f"Value {timeInMs} ms out of supported range")

