import os
from lxml import etree
from typing import Tuple, List


class IoddValidator:
    xsi_ns = "http://www.w3.org/2001/XMLSchema-instance"

    @staticmethod
    def validateXmlSchema(iodd_xml_file_path: str, xsd_schema_dir_path: str) -> Tuple[bool, List[str]]:
        iodd_xml_doc = etree.parse(iodd_xml_file_path)
        root = iodd_xml_doc.getroot()

        schema_location_attr = f"{{{IoddValidator.xsi_ns}}}schemaLocation"

        schema_location = root.attrib.get(schema_location_attr)
        if not schema_location:
            raise ValueError("Invalid IODD file: xsi:schemaLocation not found")

        # e.g. "http://www.io-link.com/IODD/2010/10 IODD1.1.xsd"
        parts = schema_location.strip().split()
        if len(parts) != 2:
            raise ValueError("Invalid IODD file: schema: expecting namespace and xsd file")
        xsd_filename = parts[1]

        # check if schema dir exists
        schema_dir = os.path.abspath(xsd_schema_dir_path) + os.path.sep
        if not os.path.isdir(schema_dir):
            raise FileNotFoundError(schema_dir)
        xsd_filename_path = os.path.join(schema_dir, xsd_filename)

        with open(xsd_filename_path, encoding='utf-8') as f:
            xsd_doc = etree.parse(f, base_url=schema_dir)
            xml_schema = etree.XMLSchema(xsd_doc)

            is_valid = xml_schema.validate(iodd_xml_doc)
            messages = []
            for error in xml_schema.error_log:
                messages.append(f"Line {error.line}: {error.message}")

            return is_valid, messages
