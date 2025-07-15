from enum import Enum
from typing import Optional


class ImageExtension(Enum):
    JPG = ('jpg', 'image/jpeg')
    JPEG = ('jpeg', 'image/jpeg')
    PNG = ('png', 'image/png')
    GIF = ('gif', 'image/gif')
    SVG = ('svg', 'image/svg+xml')
    WEBP = ('webp', 'image/webp')
    BMP = ('bmp', 'image/bmp')

    def __init__(self, extension: str, mime_type: str):
        self.extension = extension
        self.mime_type = mime_type

    @classmethod
    def from_extension(cls, extension: str) -> Optional['ImageExtension']:
        if not extension:
            return None

        normalized_extension = extension.lower().lstrip('.')

        for ext_type in cls:
            if ext_type.extension == normalized_extension:
                return ext_type
        return None

    @classmethod
    def get_mime_type(cls, extension: str) -> str:
        ext_type = cls.from_extension(extension)
        if ext_type:
            return ext_type.mime_type
        return f"image/{extension.lower().lstrip('.')}"

    @classmethod
    def get_all_extensions(cls) -> set[str]:
        return {ext_type.extension for ext_type in cls}