from dataclasses import dataclass

from dev_blumek_upload_handler.domain.types.image_extension import ImageExtension


@dataclass(frozen=True)
class StoreMetadataRequest:
    workflow_id: str
    image_key: str
    image_name: str
    image_extension: ImageExtension
    prompt: str


@dataclass(frozen=True)
class StoreMetadataReply:
    id: str
