from dataclasses import dataclass

from dev_blumek_thumbnail_generator.domain.types.image_extension import ImageExtension


@dataclass(frozen=True)
class RetrieveImageGatewayRequest:
    image_key: str


@dataclass(frozen=True)
class RetrieveImageGatewayReply:
    image_name: str
    image_extension: ImageExtension
    image_bytes: bytes
