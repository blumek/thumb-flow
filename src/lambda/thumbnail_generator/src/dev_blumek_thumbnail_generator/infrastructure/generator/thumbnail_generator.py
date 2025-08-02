from abc import abstractmethod, ABC

from dev_blumek_thumbnail_generator.infrastructure.generator.thumbnail_generator_model import (
    GenerateThumbnailRequest,
    GenerateThumbnailReply,
)


class ThumbnailGenerator(ABC):
    @abstractmethod
    def generate_thumbnail(
        self, request: GenerateThumbnailRequest
    ) -> GenerateThumbnailReply:
        pass
