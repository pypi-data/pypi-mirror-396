from typing import Tuple
from ._internal import MSeqPDSizeCombination
from iolink_utils.exceptions import InvalidMSeqCodePDSizeCombination, InvalidMSeqCode


class ODOctetCount:
    """ Use this class to find the number of on-request data octets for
        an m-sequence code (preoperate) or
        a combination of m-sequence code and ProcessData (in/out) size (operate).
    """
    # Table A.8  - M-sequence types for the PREOPERATE mode
    __preoperate = {
        #  m-sequence code: On-request data, type
        0: (1, 'TYPE_0'), # not recommended
        1: (2, 'TYPE_1_2'),
        2: (8, 'TYPE_1_V'),
        3: (32, 'TYPE_1_V')
    }

    # Table A.10 - M-sequence types for the OPERATE mode
    __operate = {
        # m-sequence code, PDin, PDout: On-request data, type
        MSeqPDSizeCombination(0, 0, 0): (1, 'TYPE_0'),
        MSeqPDSizeCombination(1, 0, 0): (2, 'TYPE_1_2'),
        MSeqPDSizeCombination(6, 0, 0): (8, 'TYPE_1_V'),
        MSeqPDSizeCombination(7, 0, 0): (32, 'TYPE_1_V'),
        MSeqPDSizeCombination(0, range(3, 32 + 1), range(0, 32 + 1)): (2, 'TYPE_1_1'),
        MSeqPDSizeCombination(0, range(0, 32 + 1), range(3, 32 + 1)): (2, 'TYPE_1_1'),
        MSeqPDSizeCombination(0, 1, 0): (1, 'TYPE_2_1'),
        MSeqPDSizeCombination(0, 2, 0): (1, 'TYPE_2_2'),
        MSeqPDSizeCombination(0, 0, 1): (1, 'TYPE_2_3'),
        MSeqPDSizeCombination(0, 0, 2): (1, 'TYPE_2_4'),
        MSeqPDSizeCombination(0, 1, 1): (1, 'TYPE_2_5'),
        MSeqPDSizeCombination(0, 2, range(1, 2 + 1)): (1, 'TYPE_2_V'),
        MSeqPDSizeCombination(0, range(1, 2 + 1), 2): (1, 'TYPE_2_V'),
        MSeqPDSizeCombination(4, range(0, 32 + 1), range(3, 32 + 1)): (1, 'TYPE_2_V'),
        MSeqPDSizeCombination(4, range(3, 32 + 1), range(0, 32 + 1)): (1, 'TYPE_2_V'),
        MSeqPDSizeCombination(5, range(1, 32 + 1), range(0, 32 + 1)): (2, 'TYPE_2_V'),
        MSeqPDSizeCombination(5, range(0, 32 + 1), range(1, 32 + 1)): (2, 'TYPE_2_V'),
        MSeqPDSizeCombination(6, range(1, 32 + 1), range(0, 32 + 1)): (8, 'TYPE_2_V'),
        MSeqPDSizeCombination(6, range(0, 32 + 1), range(1, 32 + 1)): (8, 'TYPE_2_V'),
        MSeqPDSizeCombination(7, range(1, 32 + 1), range(0, 32 + 1)): (32, 'TYPE_2_V'),
        MSeqPDSizeCombination(7, range(0, 32 + 1), range(1, 32 + 1)): (32, 'TYPE_2_V')
    }

    @staticmethod
    def in_preoperate(m_sequence_code: int) -> Tuple[int, str]:
        if m_sequence_code in ODOctetCount.__preoperate:
            return ODOctetCount.__preoperate[m_sequence_code]
        raise InvalidMSeqCode(f"Invalid m-sequence code: {m_sequence_code}. "
                              f"Allowed values are: {list(ODOctetCount.__preoperate.keys())}")

    @staticmethod
    def in_operate(m_sequence_code: int, size_PDin: int, size_PDout: int) -> Tuple[int, str]:
        for combination, value in ODOctetCount.__operate.items():
            if combination.matches(m_sequence_code, size_PDin, size_PDout):
                return value
        raise InvalidMSeqCodePDSizeCombination(f"Invalid combination of m-sequence code and "
                                               f"PD size ({m_sequence_code}, {size_PDin}, {size_PDout})")
