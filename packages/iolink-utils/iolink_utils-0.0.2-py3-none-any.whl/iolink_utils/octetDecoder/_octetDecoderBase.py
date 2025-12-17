import ctypes
from iolink_utils.exceptions import InvalidOctetValue


class OctetDecoderBase(ctypes.BigEndianStructure):
    """Base class for octet decoder (decoding a single byte)"""
    _pack_ = 1

    def __init__(self, value: int = 0):
        super().__init__()
        self.set(value)

    def __int__(self):
        """Get underlying integer value (octet) when casting instance (e.g. int(myDecoder)"""
        return int.from_bytes(bytes(self), "big")

    def get(self) -> int:
        """Get octet as integer value"""
        return int(self)

    def set(self, value: int):
        """
        Set the underlying byte (octet) value.

        Parameters
        ----------
        value : int
            An integer between 0 and 255 representing the new byte value.

        Raises
        ------
        InvalidOctetValue
            If `value` is outside the valid byte range (0–255).
        """
        _MAX_OCTET_VALUE = 255
        if 0 <= value <= _MAX_OCTET_VALUE:
            ctypes.memmove(ctypes.addressof(self), ctypes.byref(ctypes.c_uint8(value)), 1)
        else:
            raise InvalidOctetValue()

    def __repr__(self):  # pragma: no cover
        """String representation of decoded content."""
        fields_repr = ", ".join(
            f"{name}={getattr(self, name)}" for name, *_ in self._fields_ if name != 'unused'
        )
        return f"{self.__class__.__name__}({fields_repr})"
