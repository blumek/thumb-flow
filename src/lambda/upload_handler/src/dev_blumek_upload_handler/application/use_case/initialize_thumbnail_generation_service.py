from dev_blumek_upload_handler.application.use_case.initialize_thumbnail_generation_use_case import (
    InitializeThumbnailGenerationUseCase,
)
from dev_blumek_upload_handler.application.use_case.initialize_thumbnail_generation_use_case_model import (
    InitializeThumbnailGenerationUseCaseRequest,
    InitializeThumbnailGenerationUseCaseReply,
)
from dev_blumek_upload_handler.infrastructure.factory.thumbnail_generation_identifier_factory import (
    WorkflowIdentifierFactory,
)
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway import (
    ImagePersistenceGateway,
)
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway_model import (
    StoreImageGatewayRequest,
    StoreImageGatewayReply,
)
from dev_blumek_upload_handler.infrastructure.gateway.metadata_persistence_gateway import (
    MetadataPersistenceGateway,
)
from dev_blumek_upload_handler.infrastructure.gateway.metadata_perstistence_gateway_model import (
    StoreMetadataGatewayRequest,
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
        workflow_identifier_factory: WorkflowIdentifierFactory,
        image_persistence_gateway: ImagePersistenceGateway,
        metadata_persistence_gateway: MetadataPersistenceGateway,
        event_publisher: EventPublisher,
    ) -> None:
        self.workflow_identifier_factory = workflow_identifier_factory
        self.image_persistence_gateway = image_persistence_gateway
        self.metadata_persistence_gateway = metadata_persistence_gateway
        self.event_publisher = event_publisher

    def upload_image(
        self, request: InitializeThumbnailGenerationUseCaseRequest
    ) -> InitializeThumbnailGenerationUseCaseReply:
        workflow_id = self.workflow_identifier_factory.create_identifier()

        store_image_gateway_request: StoreImageGatewayRequest = (
            self.__to_store_image_gateway_request(workflow_id, request)
        )
        store_image_gateway_reply: StoreImageGatewayReply = (
            self.image_persistence_gateway.store(store_image_gateway_request)
        )

        store_metadata_gateway_request: StoreMetadataGatewayRequest = (
            self.__to_store_metadata_gateway_request(
                workflow_id, request, store_image_gateway_reply
            )
        )
        self.metadata_persistence_gateway.store(store_metadata_gateway_request)

        self.event_publisher.publish(
            self.to_event(workflow_id, request, store_image_gateway_reply)
        )
        return InitializeThumbnailGenerationUseCaseReply(
            workflow_id=workflow_id, image_key=store_image_gateway_reply.image_key
        )

    @staticmethod
    def __to_store_metadata_gateway_request(
        workflow_id: str,
        request: InitializeThumbnailGenerationUseCaseRequest,
        store_image_gateway_reply: StoreImageGatewayReply,
    ) -> StoreMetadataGatewayRequest:
        return StoreMetadataGatewayRequest(
            image_key=store_image_gateway_reply.image_key,
            image_name=request.image_name,
            image_extension=request.image_extension,
            prompt=request.prompt,
            workflow_id=workflow_id,
        )

    @staticmethod
    def __to_store_image_gateway_request(
        workflow_id: str, request: InitializeThumbnailGenerationUseCaseRequest
    ) -> StoreImageGatewayRequest:
        return StoreImageGatewayRequest(
            workflow_id=workflow_id,
            image_name=request.image_name,
            image_extension=request.image_extension,
            image_bytes=request.image_bytes,
        )

    @staticmethod
    def to_event(
        workflow_id: str,
        request: InitializeThumbnailGenerationUseCaseRequest,
        reply: StoreImageGatewayReply,
    ) -> ThumbnailGenerationRequestedEvent:
        return ThumbnailGenerationRequestedEvent(
            workflow_id=workflow_id,
            uploaded_image_key=reply.image_key,
            prompt=request.prompt,
        )
