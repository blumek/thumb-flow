import logging
from abc import ABC, abstractmethod

from infrastructure.repository.image_repository_model import (
    StoreImageRequest,
    StoreImageReply,
)

logger = logging.getLogger(__name__)


class ImageRepository(ABC):
    @abstractmethod
    def store(self, request: StoreImageRequest) -> StoreImageReply:
        pass
