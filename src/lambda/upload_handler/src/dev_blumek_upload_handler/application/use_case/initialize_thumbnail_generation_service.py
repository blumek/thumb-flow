from dev_blumek_upload_handler.application.use_case.initialize_thumbnail_generation_use_case import (
    InitializeThumbnailGenerationUseCase,
)
from dev_blumek_upload_handler.application.use_case.initialize_thumbnail_generation_use_case_model import (
    InitializeThumbnailGenerationUseCaseRequest,
    InitializeThumbnailGenerationUseCaseReply,
)
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway import (
    ImagePersistenceGateway,
)
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway_model import (
    StoreImageGatewayRequest,
    StoreImageGatewayReply,
)
from dev_blumek_upload_handler.infrastructure.messaging.event_publisher import (
    EventPublisher,
)
from dev_blumek_upload_handler.infrastructure.messaging.thumbnail_generation_requested_event import (
    ThumbnailGenerationRequestedEvent,
)


class InitializeThumbnailGenerationService(InitializeThumbnailGenerationUseCase):
    def __init__(
        self,
        image_persistence_gateway: ImagePersistenceGateway,
        event_publisher: EventPublisher,
    ) -> None:
        self.image_persistence_gateway = image_persistence_gateway
        self.event_publisher = event_publisher

    def upload_image(
        self, request: InitializeThumbnailGenerationUseCaseRequest
    ) -> InitializeThumbnailGenerationUseCaseReply:
        store_image_gateway_request: StoreImageGatewayRequest = (
            self.__to_store_image_gateway_request(request)
        )
        reply: StoreImageGatewayReply = self.image_persistence_gateway.store(
            store_image_gateway_request
        )

        self.event_publisher.publish(self.to_event(request, reply))
        return InitializeThumbnailGenerationUseCaseReply(image_key=reply.image_key)

    @staticmethod
    def __to_store_image_gateway_request(
        request: InitializeThumbnailGenerationUseCaseRequest,
    ) -> StoreImageGatewayRequest:
        return StoreImageGatewayRequest(
            image_name=request.image_name,
            image_extension=request.image_extension,
            image_bytes=request.image_bytes,
        )

    @staticmethod
    def to_event(
        request: InitializeThumbnailGenerationUseCaseRequest,
        reply: StoreImageGatewayReply,
    ) -> ThumbnailGenerationRequestedEvent:
        return ThumbnailGenerationRequestedEvent(
            uploaded_image_key=reply.image_key, prompt=request.prompt
        )
