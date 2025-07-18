from abc import ABC, abstractmethod

from infrastructure.gateway.image_persistence_gateway_model import (
    StoreImageGatewayRequest,
    StoreImageGatewayReply,
)


class ImagePersistenceGateway(ABC):
    @abstractmethod
    def store(self, request: StoreImageGatewayRequest) -> StoreImageGatewayReply:
        pass


class InvalidImageStoreRequestError(RuntimeError):
    pass
