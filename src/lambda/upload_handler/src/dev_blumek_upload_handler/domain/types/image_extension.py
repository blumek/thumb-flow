from enum import Enum
from typing import Optional


class ImageExtension(Enum):
    JPG = ("jpg", "image/jpeg")
    JPEG = ("jpeg", "image/jpeg")
    PNG = ("png", "image/png")
    GIF = ("gif", "image/gif")
    SVG = ("svg", "image/svg+xml")
    WEBP = ("webp", "image/webp")
    BMP = ("bmp", "image/bmp")

    def __init__(self, extension: str, mime_type: str):
        self.extension = extension
        self.mime_type = mime_type

    @classmethod
    def from_extension(cls, extension: str) -> Optional["ImageExtension"]:
        if not extension:
            return None

        normalized_extension = extension.lower().lstrip(".")

        for ext_type in cls:
            if ext_type.extension == normalized_extension:
                return ext_type
        return None
