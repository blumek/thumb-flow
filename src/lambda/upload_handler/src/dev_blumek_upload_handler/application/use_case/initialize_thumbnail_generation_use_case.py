from abc import ABC, abstractmethod

from dev_blumek_upload_handler.application.use_case.initialize_thumbnail_generation_use_case_model import (
    InitializeThumbnailGenerationUseCaseRequest,
    InitializeThumbnailGenerationUseCaseReply,
)


class InitializeThumbnailGenerationUseCase(ABC):
    @abstractmethod
    def upload_image(
        self, request: InitializeThumbnailGenerationUseCaseRequest
    ) -> InitializeThumbnailGenerationUseCaseReply:
        pass
