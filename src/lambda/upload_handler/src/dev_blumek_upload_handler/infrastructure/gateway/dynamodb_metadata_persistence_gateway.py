from dev_blumek_upload_handler.infrastructure.gateway.metadata_persistence_gateway import (
    MetadataPersistenceGateway,
)

from dev_blumek_upload_handler.infrastructure.gateway.metadata_perstistence_gateway_model import (
    StoreMetadataGatewayRequest,
    StoreMetadataGatewayReply,
)
from dev_blumek_upload_handler.infrastructure.repository.metadata_repository import (
    MetadataRepository,
)
from dev_blumek_upload_handler.infrastructure.repository.metadata_repository_model import (
    StoreMetadataRequest,
    StoreMetadataReply,
)


class DynamoDBMetadataPersistenceGateway(MetadataPersistenceGateway):
    def __init__(self, metadata_repository: MetadataRepository):
        self.metadata_repository = metadata_repository

    def store(
        self, store_metadata_request: StoreMetadataGatewayRequest
    ) -> StoreMetadataGatewayReply:
        request: StoreMetadataRequest = self.__to_repository_request(
            store_metadata_request
        )
        reply: StoreMetadataReply = self.metadata_repository.store(request)
        return self.__to_gateway_reply(reply)

    @staticmethod
    def __to_repository_request(
        store_metadata_request: StoreMetadataGatewayRequest,
    ) -> StoreMetadataRequest:
        return StoreMetadataRequest(
            workflow_id=store_metadata_request.workflow_id,
            image_key=store_metadata_request.image_key,
            image_name=store_metadata_request.image_name,
            image_extension=store_metadata_request.image_extension,
            prompt=store_metadata_request.prompt,
        )

    @staticmethod
    def __to_gateway_reply(
        store_metadata_reply: StoreMetadataReply,
    ) -> StoreMetadataGatewayReply:
        return StoreMetadataGatewayReply(id=store_metadata_reply.id)
