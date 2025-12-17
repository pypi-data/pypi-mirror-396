from typing import List
from iolink_utils.definitions.profiles import ProfileID


class SupportedAccessLocks:
    def __init__(self):
        self.parameter = False
        self.dataStorage = False
        self.localParameterization = False
        self.localUserInterface = False

    def __str__(self):  # pragma: no cover
        return (
            f"SupportedAccessLocks("
            f"parameter={self.parameter}, "
            f"dataStorage={self.dataStorage}, "
            f"localParameterization={self.localParameterization}, "
            f"localUserInterface={self.localUserInterface})"
        )


class Features:
    def __init__(self):
        self.blockParameter: bool = False
        self.dataStorage: bool = False
        self.profileIDs: List[ProfileID] = []
        self.supportedAccessLocks: SupportedAccessLocks = SupportedAccessLocks()

    def __str__(self):  # pragma: no cover
        return (
            f"Features("
            f"blockParameter={self.blockParameter}, "
            f"dataStorage={self.dataStorage}, "
            f"profileIDs=[{', '.join(f'{i.name}({i.value})' for i in self.profileIDs)}], \n"
            f"           {self.supportedAccessLocks}"
            f")"
        )
