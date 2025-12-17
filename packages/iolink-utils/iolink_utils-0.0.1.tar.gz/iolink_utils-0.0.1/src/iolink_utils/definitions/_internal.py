from dataclasses import dataclass
from typing import Union
from enum import EnumMeta


@dataclass(frozen=True)
class MSeqPDSizeCombination:
    m_sequence_code: int = 0
    size_PDin: Union[int, range] = 0
    size_PDout: Union[int, range] = 0

    def matches(self, m_sequence_code: int, size_PDin: int, size_PDout: int) -> bool:
        match_code = m_sequence_code == self.m_sequence_code
        match_PDin = size_PDin in self.size_PDin if isinstance(self.size_PDin, range) else size_PDin == self.size_PDin
        match_PDout = size_PDout in self.size_PDout if isinstance(self.size_PDout, range) else size_PDout == self.size_PDout
        return match_code and match_PDin and match_PDout


class AutoNameConvertMeta(EnumMeta):
    def __call__(cls, value, *args, **kwargs):
        if isinstance(value, str):
            # resolve by name
            try:
                return cls[value]
            except KeyError:
                pass
            # resolve by int string
            try:
                value = int(value)
            except ValueError:
                raise ValueError(f"Cannot convert '{value}' to {cls.__name__}")
        return super().__call__(value, *args, **kwargs)
