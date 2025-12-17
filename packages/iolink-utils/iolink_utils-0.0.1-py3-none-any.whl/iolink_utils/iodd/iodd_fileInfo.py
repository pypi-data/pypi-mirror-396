from typing import Optional
from datetime import date, datetime
from pathlib import Path
import re
from iolink_utils.utils.version import Version


class IoddFileInfo:
    # <vendor name>-<device name>-<release date>-IODD<schema version>.xml
    def __init__(self, filename: str):
        path = Path(filename).resolve()
        self.filename: str = str(path.name)
        self.fileExists: bool = path.is_file()
        if self.fileExists:
            self.dirPath: str = str(path.parent)
            self.fullPathFilename: str = str(path)
            self.sizeInBytes: int = path.stat().st_size
        else:
            self.dirPath: str = ''
            self.fullPathFilename: str = ''
            self.sizeInBytes: int = 0
        self.date: Optional[date] = None
        self.schemaVersion: Version = Version()

        match = re.search(r"-(\d{8})-IODD(\d+(?:\.\d+)*)(?:-[a-z]{2})?\.xml", filename)
        if match:
            self.date = datetime.strptime(match.group(1), "%Y%m%d").date()
            self.schemaVersion = Version(match.group(2))

    def __str__(self):  # pragma: no cover
        return (
            f"IoddFileInfo("
            f"fullPathFilename={self.fullPathFilename}, "
            f"fileExists={self.fileExists}, "
            f"sizeInBytes={self.sizeInBytes}, "
            f"date={self.date}, "
            f"schemaVersion={self.schemaVersion}"
            f")"
        )
