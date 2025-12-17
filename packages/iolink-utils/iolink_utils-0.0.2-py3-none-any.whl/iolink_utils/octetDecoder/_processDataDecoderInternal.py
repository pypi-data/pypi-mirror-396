from typing import Dict
import ctypes

_safetyCodeOutFields = [
    ("FO_CRC", ctypes.c_uint32),
    ("FO_ChFAckReq", ctypes.c_uint8, 1),
    ("FO_SetSD", ctypes.c_uint8, 1),
    ("unused", ctypes.c_uint8, 3),
    ("FO_MCNT", ctypes.c_uint8, 3),
    ("FO_portNum", ctypes.c_uint8)
]

_safetyCodeInFields = [
    ("FI_CRC", ctypes.c_uint32),
    ("FI_DTimeout", ctypes.c_uint8, 1),
    ("FI_DCommError", ctypes.c_uint8, 1),
    ("FI_SDset", ctypes.c_uint8, 1),
    ("unused", ctypes.c_uint8, 2),
    ("FI_DCNT", ctypes.c_uint8, 3),
    ("FI_portNum", ctypes.c_uint8)
]

def __sortByBitOffset(elem: Dict):
    return elem['bitOffset']


def __get_filler(bit_count: int):
    filler = []
    count = int((bit_count + 8 - 1) / 8)

    for idx in range(count):
        filler_bit_count = bit_count if bit_count <= 8 else 8
        filler.append(("unused", ctypes.c_uint8, filler_bit_count))
        bit_count -= 8

    filler.reverse()
    return filler


def __create_field_from_data_format(json_dataFormat, safetyCodeFields):
    # Goes through all elements of the data format and creates fields with the specified length.
    # Sometimes we need to add a filler to bridge unused bits.
    fields = []

    bit_offset = 0
    for element in json_dataFormat:
        e_name = element['name'][0] #  using textId as name
        e_offset = element['bitOffset']
        e_value_type = element['data']['type']
        e_length = element['data']['bitLength']
        e_subIndex = element['subIndex'] if 'subIndex' in element else 0

        diff = e_offset - bit_offset
        if diff > 0:
            # element is not at end of last element -> add filler
            filler = __get_filler(diff)
            fields.extend(filler)
            bit_offset += diff

        if e_value_type == bytearray:
            if e_subIndex == 127 and e_length == 6*8:  # safety code has 6 bytes (crc32)
                fields.extend(safetyCodeFields)
            else:
                if e_length % 8 != 0:
                    raise ValueError(f"Invalid bit count: {e_length} (not a multiple of 8)")
                fields.append((e_name, ctypes.c_ubyte * int(e_length / 8)))
        else:
            if e_length <= 8:
                fields.append((e_name, ctypes.c_uint8, e_length))
            elif e_length <= 16:
                fields.append((e_name, ctypes.c_uint16, e_length))
            elif e_length <= 32:
                fields.append((e_name, ctypes.c_uint32, e_length))
            else:
                raise ValueError(f"Invalid length ({e_length}) for {e_name}")

        bit_offset += e_length

    fields.reverse()
    field_names = [field[0] for field in fields if field[0] != 'unused']

    return fields, field_names


def _createPDDecoderClass(json_dataFormat, safetyCodeFields):
    json_dataFormat.sort(reverse=False, key=__sortByBitOffset)
    fields, field_names = __create_field_from_data_format(json_dataFormat, safetyCodeFields)

    base = ctypes.BigEndianStructure
    attrs = {"_pack_": 1, "_fields_": fields, "field_names": field_names}
    return type("PDDecoder", (base,), attrs)
