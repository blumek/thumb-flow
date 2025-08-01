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
            raise ValueError("No extension provided")

        normalized_extension = extension.lower().lstrip(".")

        for ext_type in cls:
            if ext_type.extension == normalized_extension:
                return ext_type

        raise Exception(f"Unknown extension: {extension}")

    @classmethod
    def from_mime_type(cls, mime_type: str) -> Optional["ImageExtension"]:
        if not mime_type:
            raise ValueError("No MIME type provided")

        normalized_mime_type = mime_type.lower()

        for ext_type in cls:
            if ext_type.mime_type == normalized_mime_type:
                return ext_type

        raise Exception(f"Unknown MIME type: {mime_type}")
