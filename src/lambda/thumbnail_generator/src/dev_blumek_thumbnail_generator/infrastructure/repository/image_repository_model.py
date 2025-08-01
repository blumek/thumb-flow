from dataclasses import dataclass

from dev_blumek_thumbnail_generator.domain.types.image_extension import ImageExtension


@dataclass(frozen=True)
class RetrieveImageRequest:
    image_key: str


@dataclass(frozen=True)
class RetrieveImageReply:
    image_name: str
    image_extension: ImageExtension
    image_bytes: bytes


@dataclass(frozen=True)
class StoreImageRequest:
    image_key: str
    image_extension: ImageExtension
    image_bytes: bytes


@dataclass(frozen=True)
class StoreImageReply:
    image_key: str
