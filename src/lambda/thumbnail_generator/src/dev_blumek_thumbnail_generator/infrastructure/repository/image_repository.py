import logging
from abc import ABC, abstractmethod

from dev_blumek_thumbnail_generator.infrastructure.repository.image_repository_model import (
    StoreImageRequest,
    StoreImageReply,
    RetrieveImageRequest,
    RetrieveImageReply,
)

logger = logging.getLogger(__name__)


class ImageRepository(ABC):
    @abstractmethod
    def retrieve(self, request: RetrieveImageRequest) -> RetrieveImageReply:
        pass

    @abstractmethod
    def store(self, request: StoreImageRequest) -> StoreImageReply:
        pass
