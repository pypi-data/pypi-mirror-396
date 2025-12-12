from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class FileKind(str, Enum):
    UNKNOWN = 'unknown'
    TEXT = 'text/plain'
    BINARY = 'application/octet-stream'
    PDF = 'application/pdf'
    MS_WORD = 'application/msword'
    MS_WORDX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    MS_EXCEL = 'application/vnd.ms-excel'
    MS_EXCELX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    CSV = 'text/csv'
    JSON = 'application/json'
    XML = 'application/xml'
    HTML = 'text/html'
    MARKDOWN = 'text/markdown'
    IMAGE_PNG = 'image/png'
    IMAGE_JPEG = 'image/jpeg'
    IMAGE_GIF = 'image/gif'
    IMAGE_BMP = 'image/bmp'
    IMAGE_TIFF = 'image/tiff'
    IMAGE_WEBP = 'image/webp'
    IMAGE_SVG = 'image/svg+xml'
    ZIP = 'application/zip'
    GZIP = 'application/gzip'
    TAR = 'application/x-tar'
    BZIP2 = 'application/x-bzip2'
    XZ = 'application/x-xz'
    SEVEN_Z = 'application/x-7z-compressed'
    RAR = 'application/x-rar-compressed'
    EXECUTABLE = 'application/x-executable'
    ELF = 'application/x-elf'
    SHELL_SCRIPT = 'text/x-shellscript'
    PYTHON = 'text/x-python'
    JS = 'application/javascript'
    CHEM_SDF = 'chemical/x-mdl-sdfile'
    CHEM_MOL = 'chemical/x-mdl-molfile'
    CHEM_MOL2 = 'chemical/x-mol2'

class BizFileKind(Enum):
    GENERIC_TEXT = ...
    GENERIC_BINARY = ...
    DOCUMENT = ...
    IMAGE = ...
    ARCHIVE = ...
    EXECUTABLE = ...
    CHEM_STRUCTURE = ...
    DATA_TABLE = ...
    CONFIG_OR_CODE = ...
    UNKNOWN = ...

@dataclass
class FileTypeInfo:
    path: Path
    exists: bool
    is_file: bool
    size: int
    kind: FileKind
    mime: str
    biz_kind: BizFileKind
    encoding: str | None
    is_text: bool
    used_magic: bool
    reason: str

def detect_file_type(path: str | Path) -> FileTypeInfo: ...
