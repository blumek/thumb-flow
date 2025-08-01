from dev_blumek_upload_handler.application.use_case.image_upload_use_case import (
    UploadImageUseCase,
)
from dev_blumek_upload_handler.application.use_case.image_upload_use_case_model import (
    StoreImageUseCaseRequest,
    StoreImageUseCaseReply,
)
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway import (
    ImagePersistenceGateway,
)
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway_model import (
    StoreImageGatewayRequest,
    StoreImageGatewayReply,
)


class UploadImageService(UploadImageUseCase):
    def __init__(self, image_persistence_gateway: ImagePersistenceGateway):
        self.image_persistence_gateway = image_persistence_gateway

    def upload_image(self, request: StoreImageUseCaseRequest) -> StoreImageUseCaseReply:
        store_image_gateway_request: StoreImageGatewayRequest = (
            self.__to_store_image_gateway_request(request)
        )
        reply: StoreImageGatewayReply = self.image_persistence_gateway.store(
            store_image_gateway_request
        )
        return StoreImageUseCaseReply(image_key=reply.image_key)

    @staticmethod
    def __to_store_image_gateway_request(
        request: StoreImageUseCaseRequest,
    ) -> StoreImageGatewayRequest:
        return StoreImageGatewayRequest(
            image_name=request.image_name,
            image_extension=request.image_extension,
            image_bytes=request.image_bytes,
        )
