from dataclasses import dataclass

from dev_blumek_upload_handler.domain.types.image_extension import ImageExtension


@dataclass(frozen=True)
class StoreImageGatewayRequest:
    image_name: str
    image_extension: ImageExtension
    image_bytes: bytes


@dataclass(frozen=True)
class StoreImageGatewayReply:
    image_key: str
