from typing import Dict, Tuple

from .iodd_fileInfo import IoddFileInfo
from ._internal.iodd_documentInfo import DocumentInfo
from ._internal.iodd_identity import Identity
from ._internal.iodd_features import Features
from ._internal.iodd_physical_layer import PhysicalLayer
from ._internal.iodd_xmlDoc import IoddXmlDoc

from iolink_utils.definitions.onRequestDataOctetCount import ODOctetCount
from iolink_utils.definitions.profiles import ProfileID
from iolink_utils.exceptions import IoddFileNotFound, InvalidIoddFile, MSequenceCapabilityMissing


class Iodd:
    def __init__(self, iodd_xml_file_path: str):
        self.fileInfo: IoddFileInfo = IoddFileInfo(iodd_xml_file_path)

        if not self.fileInfo.fileExists:
            raise IoddFileNotFound(f"IODD file not found: {self.fileInfo.fullPathFilename}")

        iodd_xml_doc = IoddXmlDoc(self.fileInfo.fullPathFilename)
        if iodd_xml_doc.docType == 'IODevice':
            self.documentInfo: DocumentInfo = iodd_xml_doc.get_document_info()
            self.identity: Identity = iodd_xml_doc.get_identity()
            self.features: Features = iodd_xml_doc.get_device_features()
            self.physicalLayer: PhysicalLayer = iodd_xml_doc.get_physical_layer()
            self.processDataDefinition: Dict = iodd_xml_doc.get_process_data_definition()
        else:
            raise InvalidIoddFile(f"Expected IODevice inside XML file, got {iodd_xml_doc.docType}.")

    def isSafetyDevice(self) -> bool:
        return ProfileID.SafetyDevice in self.features.profileIDs

    @property
    def processDataConditionValues(self) -> list:
        return list(self.processDataDefinition.keys())

    @property
    def size_PDin(self) -> int:
        # note: by spec all process data definitions need to have the same size
        condition = self.processDataConditionValues[0]
        if 'pdIn' in self.processDataDefinition[condition]:
            return int(self.processDataDefinition[condition]['pdIn']['bitLength'] / 8)
        else:
            return 0

    @property
    def size_PDout(self) -> int:
        # note: by spec all process data definitions need to have the same size
        condition = self.processDataConditionValues[0]
        if 'pdOut' in self.processDataDefinition[condition]:
            return int(self.processDataDefinition[condition]['pdOut']['bitLength'] / 8)
        else:
            return 0

    @property
    def size_OnRequestData(self) -> Tuple[int, int]:
        """
        Returns number of on-request data octets in PREOPERATE and OPERATE
        :return: Tuple[preoperate, operate]
        """
        if self.physicalLayer.m_sequence_capability is None:
            raise MSequenceCapabilityMissing("M-sequence capability required to calculate on-request data size.")

        ODsize_preoperate: int = ODOctetCount.in_preoperate(self.physicalLayer.m_sequence_capability.preoperateCode)[0]
        ODsize_operate: int = ODOctetCount.in_operate(
            self.physicalLayer.m_sequence_capability.operateCode, self.size_PDin, self.size_PDout)[0]
        return ODsize_preoperate, ODsize_operate

    def __str__(self):  # pragma: no cover
        return (
            f"IODD(\n"
            f"  {self.fileInfo}\n"
            f"  {self.features}\n"
            f"  {self.physicalLayer}\n"
            f")"
        )
