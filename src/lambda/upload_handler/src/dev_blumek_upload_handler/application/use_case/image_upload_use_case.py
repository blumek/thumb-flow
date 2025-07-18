from abc import ABC, abstractmethod

from dev_blumek_upload_handler.application.use_case.image_upload_use_case_model import (
    StoreImageUseCaseRequest,
    StoreImageUseCaseReply,
)


class UploadImageUseCase(ABC):
    @abstractmethod
    def upload_image(self, request: StoreImageUseCaseRequest) -> StoreImageUseCaseReply:
        pass
