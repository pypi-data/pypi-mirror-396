from typing import Tuple

from lxml import etree
from datetime import date

from .iodd_documentInfo import DocumentInfo
from .iodd_identity import Identity, DeviceVariant
from .iodd_features import Features
from .iodd_physical_layer import PhysicalLayer

from iolink_utils.utils.version import Version
from iolink_utils.definitions.bitRate import BitRate
from iolink_utils.definitions.profiles import ProfileID
from iolink_utils.octetDecoder.octetDecoder import MSequenceCapability


class IoddXmlDoc:
    def __init__(self, iodd_xml_file_path: str):
        self.iodd_xml_doc = etree.parse(iodd_xml_file_path)
        root = self.iodd_xml_doc.getroot()
        self.namespaces = {
            'iolink': root.nsmap.get(None),
            'xsi': root.nsmap.get('xsi')
        }
        self.docType = etree.QName(root).localname  # IODevice (iodd) or ExternalTextDocument (translations)

    def get_document_info(self) -> DocumentInfo:
        root = self.iodd_xml_doc.getroot()
        xml_document_info = root.find(".//iolink:DocumentInfo", namespaces=self.namespaces)

        doc_info = DocumentInfo()

        if xml_document_info is not None:
            doc_info.version = Version(xml_document_info.get("version"))
            doc_info.releaseDate = date.fromisoformat(xml_document_info.get("releaseDate").strip())
            doc_info.copyright = xml_document_info.get("copyright")

        return doc_info

    def get_identity(self) -> Identity:
        root = self.iodd_xml_doc.getroot()
        xml_identity = root.find(".//iolink:DeviceIdentity", namespaces=self.namespaces)

        identity = Identity()

        if xml_identity is not None:
            identity.vendorId = int(xml_identity.get("vendorId"))
            identity.deviceId = int(xml_identity.get("deviceId"))
            identity.vendorName = xml_identity.get("vendorName")

            identity.vendorText = self.__getTextTuple(xml_identity, 'VendorText')
            identity.vendorUrl = self.__getTextTuple(xml_identity, 'VendorUrl')
            xml_vendorLogo = xml_identity.find(".//iolink:VendorLogo", namespaces=self.namespaces)
            identity.vendorLogo = "" if xml_vendorLogo is None else xml_vendorLogo.get('name')
            identity.deviceName = self.__getTextTuple(xml_identity, 'DeviceName')
            identity.deviceFamily = self.__getTextTuple(xml_identity, 'DeviceFamily')

            xml_deviceVariants = xml_identity.xpath(".//iolink:DeviceVariant", namespaces=self.namespaces)
            for xml_deviceVariant in xml_deviceVariants:
                variant = DeviceVariant()
                variant.productId = xml_deviceVariant.get('productId')
                variant.deviceSymbol = xml_deviceVariant.get('deviceSymbol')
                variant.deviceIcon = xml_deviceVariant.get('deviceIcon')
                variant.name = self.__getTextTuple(xml_deviceVariant, 'Name')
                variant.description = self.__getTextTuple(xml_deviceVariant, 'Description')
                identity.deviceVariants.append(variant)

        return identity

    def get_device_features(self) -> Features:
        root = self.iodd_xml_doc.getroot()
        xml_features = root.find(".//iolink:Features", namespaces=self.namespaces)

        features = Features()

        if xml_features is not None:
            features.blockParameter = xml_features.get("blockParameter") == "true"
            features.dataStorage = xml_features.get("dataStorage") == "true"
            features.profileIDs = [ProfileID(int(c)) for c in xml_features.get("profileCharacteristic", default='').split()]

            xml_locks = xml_features.xpath("./iolink:SupportedAccessLocks", namespaces=self.namespaces)
            if len(xml_locks) == 1:
                features.supportedAccessLocks.parameter = xml_locks[0].get("parameter")
                features.supportedAccessLocks.dataStorage = xml_locks[0].get("dataStorage")
                features.supportedAccessLocks.localParameterization = xml_locks[0].get("localParameterization")
                features.supportedAccessLocks.localUserInterface = xml_locks[0].get("localUserInterface")

        return features

    def get_physical_layer(self) -> PhysicalLayer:
        root = self.iodd_xml_doc.getroot()
        xml_physical_layer = root.find(".//iolink:PhysicalLayer", namespaces=self.namespaces)

        physical_layer = PhysicalLayer()

        if xml_physical_layer is not None:
            bitrate = xml_physical_layer.get("bitrate")
            if not bitrate:
                bitrate = xml_physical_layer.get("baudrate")
            physical_layer.bitrate = BitRate(bitrate)
            physical_layer.min_cycle_time = int(xml_physical_layer.get("minCycleTime"))
            physical_layer.sio_supported = xml_physical_layer.get("sioSupported") == "true"

            capa = xml_physical_layer.get("mSequenceCapability")
            physical_layer.m_sequence_capability = MSequenceCapability(int(capa)) if capa else None

        return physical_layer

    def get_process_data_definition(self):
        root = self.iodd_xml_doc.getroot()

        pdDefs = {}

        for xml_process_data in root.xpath(".//iolink:ProcessData", namespaces=self.namespaces):
            xml_cond = xml_process_data.find("./iolink:Condition", namespaces=self.namespaces)
            condition = None if xml_cond is None else int(xml_cond.get("value"))  # is int or bool

            processData_json = {
                'id': xml_process_data.get("id")
            }

            pdIn = xml_process_data.xpath("./iolink:ProcessDataIn", namespaces=self.namespaces)
            assert (len(pdIn) <= 1)
            if len(pdIn) == 1:
                processData_json['pdIn'] = self.__getProcessDataInOutAsJSON(pdIn[0])

            pdOut = xml_process_data.xpath("./iolink:ProcessDataOut", namespaces=self.namespaces)
            assert (len(pdOut) <= 1)
            if len(pdOut) == 1:
                processData_json['pdOut'] = self.__getProcessDataInOutAsJSON(pdOut[0])

            pdDefs[condition] = processData_json

        return pdDefs

    def __getTextTuple(self, xml_element, textXmlTag: str) -> Tuple[str, str]:
        """
        Returns the textId and corresponding text of the specified tag (e.g. VendorText, Name, Description, ...)
        :param xml_element: starting point for search
        :param textXmlTag: tag name which contains textId attribute (e.g. DeviceName)
        :return: name of textId and text
        """
        textTag = xml_element.find(f'./iolink:{textXmlTag}', namespaces=self.namespaces)
        if textTag is not None:
            text_id = textTag.attrib.get('textId')
            return text_id, self.__getTextForTextID(text_id)
        else:
            return "", ""

    def __getTextForTextID(self, text_id: str, language: str = "en") -> str:
        root = self.iodd_xml_doc.getroot()
        result = root.xpath(f"//iolink:ExternalTextCollection/"
                            f"iolink:PrimaryLanguage[@xml:lang='{language}']/iolink:Text[@id='{text_id}']/@value",
                            namespaces=self.namespaces)
        return result[0] if result else ""

    def __getDatatype(self, xml_element):
        dataType = xml_element.find("./iolink:Datatype", namespaces=self.namespaces)
        if dataType is None:
            dataType = xml_element.find("./iolink:SimpleDatatype", namespaces=self.namespaces)
            if dataType is None:
                dataTypeRef = xml_element.find("./iolink:DatatypeRef", namespaces=self.namespaces)
                if dataTypeRef is not None:
                    dataTypeId = dataTypeRef.get("datatypeId")
                    dataTypeList = self.iodd_xml_doc.getroot().xpath(f".//iolink:Datatype[@id='{dataTypeId}']",
                                                                     namespaces=self.namespaces)
                    if len(dataTypeList) == 1:
                        dataType = dataTypeList[0]
        return dataType

    def __getProcessDataInOutAsJSON(self, xml_processData):
        pd_json = {
            "id": xml_processData.get("id"),
            "bitLength": int(xml_processData.get("bitLength")),
            'name': (),
            "dataFormat": []
        }

        # name
        text_id = xml_processData.find('./iolink:Name', namespaces=self.namespaces).attrib.get('textId')
        pd_json['name'] = (text_id, self.__getTextForTextID(text_id))

        # data format
        dataType = self.__getDatatype(xml_processData)
        pd_json['dataFormat'] = self.__getDatatypeAsJSON(dataType)

        return pd_json

    def __getDatatypeAsJSON(self, xml_dataType):
        items = []
        typeName = xml_dataType.get(f"{{{self.namespaces['xsi']}}}type")

        if typeName in ['RecordT', 'ArrayT']:
            # Complex data type
            items.extend(self.__getComplexDatatypeAsJSON(xml_dataType))
        else:
            # Simple data type
            item_json = {
                'bitOffset': 0,
                'data': self.__getSimpleDatatypeAsJSON(xml_dataType)
            }
            items.append(item_json)

        return items

    def __getRecordTypeAsJSON(self, xml_record_datatype):
        items = []

        for recordItem in xml_record_datatype.xpath(".//iolink:RecordItem", namespaces=self.namespaces):
            recordItem_json = {
                'bitOffset': int(recordItem.get("bitOffset")),
                'subIndex': int(recordItem.get("subindex")),
                'name': (),
                'data': None
            }

            text_id = recordItem.find('./iolink:Name', namespaces=self.namespaces).attrib.get('textId')
            recordItem_json['name'] = (text_id, self.__getTextForTextID(text_id))

            dataType = self.__getDatatype(recordItem)
            if dataType is not None:
                recordItem_json['data'] = self.__getSimpleDatatypeAsJSON(dataType)
                items.append(recordItem_json)

        return items

    def __getArrayTypeAsJSON(self, xml_array_datatype):
        items = []

        count = int(xml_array_datatype.attrib.get('count'))
        dataType = self.__getDatatype(xml_array_datatype)
        # only SimpleDataTypes allowed inside an ArrayT
        datatype_json = self.__getSimpleDatatypeAsJSON(dataType)

        for itemNumber in range(count):
            arrayItem_json = {
                'bitOffset': int(datatype_json['bitLength']) * itemNumber,
                'data': datatype_json
            }
            items.append(arrayItem_json)

        return items

    def __getComplexDatatypeAsJSON(self, xml_complex_datatype):
        typeName = xml_complex_datatype.get(f"{{{self.namespaces['xsi']}}}type")

        if typeName == 'RecordT':
            return self.__getRecordTypeAsJSON(xml_complex_datatype)
        elif typeName == 'ArrayT':
            return self.__getArrayTypeAsJSON(xml_complex_datatype)
        else:
            raise ValueError(f"Unsupported complex data type ({typeName}).")

    def __getSimpleDatatypeAsJSON(self, xml_simple_datatype):
        datatype_json = {
            'type': None,
            'bitLength': 0
        }
        simple_datatype_name = xml_simple_datatype.get(f"{{{self.namespaces['xsi']}}}type")

        if simple_datatype_name == 'BooleanT':
            datatype_json['type'] = bool
            datatype_json['bitLength'] = 1
        elif simple_datatype_name in ['UIntegerT', 'IntegerT']:
            datatype_json['type'] = int
            datatype_json['bitLength'] = int(xml_simple_datatype.get("bitLength"))
        elif simple_datatype_name == 'Float32T':
            datatype_json['type'] = float
            datatype_json['bitLength'] = 32
        elif simple_datatype_name in ['StringT', 'OctetStringT']:
            datatype_json['type'] = bytearray
            datatype_json['bitLength'] = int(xml_simple_datatype.get("fixedLength")) * 8
        else:
            raise ValueError(f"Not supported '{simple_datatype_name}'")

        return datatype_json
