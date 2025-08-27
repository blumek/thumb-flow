from abc import ABC, abstractmethod

from dev_blumek_upload_handler.infrastructure.gateway.metadata_perstistence_gateway_model import (
    StoreMetadataGatewayReply,
    StoreMetadataGatewayRequest,
)


class MetadataPersistenceGateway(ABC):
    @abstractmethod
    def store(
        self, store_metadata_request: StoreMetadataGatewayRequest
    ) -> StoreMetadataGatewayReply:
        pass
