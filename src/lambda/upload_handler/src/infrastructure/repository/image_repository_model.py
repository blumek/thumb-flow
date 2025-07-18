from dataclasses import dataclass

from domain.types.image_extension import ImageExtension


@dataclass(frozen=True)
class StoreImageRequest:
    image_key: str
    image_extension: ImageExtension
    image_bytes: bytes


@dataclass(frozen=True)
class StoreImageReply:
    image_key: str
