from dev_blumek_thumbnail_generator.application.use_case.generate_thumbail_use_case import (
    GenerateThumbnailUseCase,
)
from dev_blumek_thumbnail_generator.application.use_case.generate_thumbail_use_case_model import (
    GenerateThumbnailUseCaseRequest,
    GenerateThumbnailUseCaseReply,
)
from dev_blumek_thumbnail_generator.infrastructure.gateway.image_persistence_gateway import (
    ImagePersistenceGateway,
)
from dev_blumek_thumbnail_generator.infrastructure.gateway.image_persistence_gateway_model import (
    StoreImageGatewayRequest,
    StoreImageGatewayReply,
)
from dev_blumek_thumbnail_generator.infrastructure.gateway.image_query_gateway import (
    ImageQueryGateway,
)
from dev_blumek_thumbnail_generator.infrastructure.gateway.image_query_gateway_model import (
    RetrieveImageGatewayReply,
    RetrieveImageGatewayRequest,
)
from dev_blumek_thumbnail_generator.infrastructure.gateway.metadata_persistence_gateway import (
    MetadataPersistenceGateway,
)
from dev_blumek_thumbnail_generator.infrastructure.gateway.metadata_perstistence_gateway_model import (
    StoreMetadataGatewayRequest,
)
from dev_blumek_thumbnail_generator.infrastructure.generator.thumbnail_generator import (
    ThumbnailGenerator,
)
from dev_blumek_thumbnail_generator.infrastructure.generator.thumbnail_generator_model import (
    GenerateThumbnailRequest,
    GenerateThumbnailReply,
)


class GenerateThumbnailService(GenerateThumbnailUseCase):
    def __init__(
        self,
        image_query_gateway: ImageQueryGateway,
        image_persistence_gateway: ImagePersistenceGateway,
        thumbnail_generator: ThumbnailGenerator,
        metadata_persistence_gateway: MetadataPersistenceGateway,
    ) -> None:
        self.image_query_gateway: ImageQueryGateway = image_query_gateway
        self.image_persistence_gateway: ImagePersistenceGateway = (
            image_persistence_gateway
        )
        self.thumbnail_generator: ThumbnailGenerator = thumbnail_generator
        self.metadata_persistence_gateway: MetadataPersistenceGateway = (
            metadata_persistence_gateway
        )

    def generate_thumbnail(
        self, request: GenerateThumbnailUseCaseRequest
    ) -> GenerateThumbnailUseCaseReply:
        image_query_reply: RetrieveImageGatewayReply = (
            self.image_query_gateway.retrieve(self.__to_retrieve_image_request(request))
        )
        generate_thumbnail_reply: GenerateThumbnailReply = (
            self.thumbnail_generator.generate_thumbnail(
                self.__to_generate_thumbnail_request(request, image_query_reply)
            )
        )
        store_image_gateway_reply = self.image_persistence_gateway.store(
            self.__to_store_image_request(
                request.workflow_id, image_query_reply, generate_thumbnail_reply
            )
        )
        store_metadata_gateway_request: StoreMetadataGatewayRequest = (
            self.__to_store_metadata_gateway_request(
                request.workflow_id, store_image_gateway_reply
            )
        )
        self.metadata_persistence_gateway.store(store_metadata_gateway_request)
        return GenerateThumbnailUseCaseReply(
            thumbnail_key=store_image_gateway_reply.image_key
        )

    @staticmethod
    def __to_retrieve_image_request(
        request: GenerateThumbnailUseCaseRequest,
    ) -> RetrieveImageGatewayRequest:
        return RetrieveImageGatewayRequest(image_key=request.image_key)

    @staticmethod
    def __to_generate_thumbnail_request(
        request: GenerateThumbnailUseCaseRequest,
        image_query_reply: RetrieveImageGatewayReply,
    ) -> GenerateThumbnailRequest:
        return GenerateThumbnailRequest(
            input_image_bytes=image_query_reply.image_bytes, prompt=request.prompt
        )

    @staticmethod
    def __to_store_image_request(
        workflow_id: str,
        image_query_reply: RetrieveImageGatewayReply,
        generate_thumbnail_reply: GenerateThumbnailReply,
    ) -> StoreImageGatewayRequest:
        return StoreImageGatewayRequest(
            workflow_id=workflow_id,
            image_name=image_query_reply.image_name,
            image_extension=image_query_reply.image_extension,
            image_bytes=generate_thumbnail_reply.thumbnail_bytes,
        )

    @staticmethod
    def __to_store_metadata_gateway_request(
        workflow_id: str,
        store_image_gateway_reply: StoreImageGatewayReply,
    ) -> StoreMetadataGatewayRequest:
        return StoreMetadataGatewayRequest(
            image_key=store_image_gateway_reply.image_key, workflow_id=workflow_id
        )
