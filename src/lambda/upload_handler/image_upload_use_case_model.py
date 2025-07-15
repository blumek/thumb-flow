from dataclasses import dataclass

from image_extension import ImageExtension


@dataclass
class StoreImageUseCaseRequest:
    image_name: str
    image_extension: ImageExtension
    image_bytes: bytes


@dataclass
class StoreImageUseCaseReply:
    image_key: str
