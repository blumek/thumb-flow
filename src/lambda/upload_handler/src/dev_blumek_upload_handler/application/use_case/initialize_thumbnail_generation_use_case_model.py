from dataclasses import dataclass

from dev_blumek_upload_handler.domain.types.image_extension import ImageExtension


@dataclass(frozen=True)
class InitializeThumbnailGenerationUseCaseRequest:
    image_name: str
    image_extension: ImageExtension
    image_bytes: bytes
    prompt: str


@dataclass(frozen=True)
class InitializeThumbnailGenerationUseCaseReply:
    workflow_id: str
    image_key: str
