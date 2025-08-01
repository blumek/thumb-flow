from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class GenerateThumbnailRequest:
    input_image_bytes: bytes
    prompt: str
    seed: Optional[int] = None


@dataclass(frozen=True)
class GenerateThumbnailReply:
    thumbnail_bytes: bytes
