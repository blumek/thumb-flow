from dev_blumek_upload_handler.infrastructure.repository.image_repository import (
    ImageRepository,
)
from dev_blumek_upload_handler.infrastructure.repository.image_repository_model import (
    StoreImageRequest,
    StoreImageReply,
)


class InMemoryImageRepository(ImageRepository):
    def __init__(self):
        self.storage: dict[str, bytes] = {}

    def store(self, request: StoreImageRequest) -> StoreImageReply:
        self.storage[request.image_key] = request.image_bytes
        return StoreImageReply(image_key=request.image_key)
