from .crcLookupTables import crc16_lookup_table, crc32_lookup_table

# See IOL SafetySpec: Figure D.4 – CRC-16 signature calculation using a lookup table
# r = crctab16 [((r >> 8) ^ *q++) & 0xff] ^(r << 8)
def crc16(data: bytearray, seed: int = 0):
    crc = seed
    for d in data:
        crc = crc16_lookup_table[((crc >> 8) & 0x00ff) ^ d] ^ ((crc << 8) & 0xff00)
    return crc & 0xffff
