from iolink_utils.definitions.fsp_ioStructDescription import FSP_IOStructDescription
from iolink_utils.exceptions import InvalidProcessDataDefinition


def createFSP_IOStructDescription(processDataDefinition: dict) -> FSP_IOStructDescription:
    description = FSP_IOStructDescription()

    if len(processDataDefinition) != 1 or None not in processDataDefinition:
        # multiple ProcessData definitions are not allowed in SafetyDevices
        raise InvalidProcessDataDefinition(f"Invalid ProcessData: for safety devices, only a "
                                           f"single definition is allowed (with key None). "
                                           f"Found {len(processDataDefinition)} definitions.")

    def _getDescription(pdDescrInOut) -> FSP_IOStructDescription.Description:
        descr = FSP_IOStructDescription.Description()

        for element in pdDescrInOut['dataFormat']:
            if element['subIndex'] == 127:
                descr.DataRange = int((pdDescrInOut['bitLength'] - element['bitOffset']) / 8)
                descr.TotalOfOctets = descr.DataRange - int(element['data']['bitLength'] / 8) # subtract size of SafetyCode
            elif element['subIndex'] < 127:
                if element['data']['bitLength'] == 1:
                    descr.TotalOfBits += 1
                elif element['data']['bitLength'] == 16:
                    descr.TotalOfInt16 += 1
                elif element['data']['bitLength'] == 32:
                    descr.TotalOfInt32 += 1
                else:
                    raise InvalidProcessDataDefinition(f"Invalid bit length in {element['name']}: "
                                                       f"{element['data']['bitLength']} (allowed: 1, 16 or 32)")
        descr.TotalOfOctets -= ((descr.TotalOfInt16 * 2) + (descr.TotalOfInt32 * 4))
        assert descr.TotalOfOctets >= 0

        return descr

    description.input = _getDescription(processDataDefinition[None]['pdIn'])
    description.output = _getDescription(processDataDefinition[None]['pdOut'])

    return description
