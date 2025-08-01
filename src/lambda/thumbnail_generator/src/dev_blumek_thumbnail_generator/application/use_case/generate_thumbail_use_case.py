from abc import ABC

from dev_blumek_thumbnail_generator.application.use_case.generate_thumbail_use_case_model import (
    GenerateThumbnailUseCaseRequest,
    GenerateThumbnailUseCaseReply,
)


class GenerateThumbnailUseCase(ABC):
    def generate_thumbnail(
        self, request: GenerateThumbnailUseCaseRequest
    ) -> GenerateThumbnailUseCaseReply:
        pass
