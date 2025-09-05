from dataclasses import dataclass


@dataclass(frozen=True)
class GenerateThumbnailUseCaseRequest:
    workflow_id: str
    image_key: str
    prompt: str


@dataclass(frozen=True)
class GenerateThumbnailUseCaseReply:
    thumbnail_key: str
