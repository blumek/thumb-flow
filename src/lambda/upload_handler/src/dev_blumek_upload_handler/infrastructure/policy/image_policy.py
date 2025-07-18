from abc import ABC, abstractmethod
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway_model import (
    StoreImageGatewayRequest,
)


class ImagePolicy(ABC):
    @abstractmethod
    def is_valid(self, image_store_request: StoreImageGatewayRequest) -> bool:
        pass
