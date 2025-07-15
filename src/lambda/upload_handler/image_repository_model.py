from dataclasses import dataclass

from image_extension import ImageExtension


@dataclass
class StoreImageRequest:
    image_key: str
    image_extension: ImageExtension
    image_bytes: bytes


@dataclass
class StoreImageReply:
    image_key: str
