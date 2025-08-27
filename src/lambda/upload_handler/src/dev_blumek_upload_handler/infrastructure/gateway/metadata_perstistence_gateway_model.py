from dataclasses import dataclass

from dev_blumek_upload_handler.domain.types.image_extension import ImageExtension


@dataclass(frozen=True)
class StoreMetadataGatewayRequest:
    workflow_id: str
    image_key: str
    image_name: str
    image_extension: ImageExtension
    prompt: str


@dataclass(frozen=True)
class StoreMetadataGatewayReply:
    id: str
