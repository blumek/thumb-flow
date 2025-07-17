from domain.types.image_extension import ImageExtension
from infrastructure.gateway.image_persistence_gateway_model import (
    StoreImageGatewayRequest,
)
from infrastructure.policy.image_policy import ImagePolicy


class ExtensionImagePolicy(ImagePolicy):
    def __init__(self, allowed_extensions: set[ImageExtension]):
        self.allowed_extensions: set[ImageExtension] = set(allowed_extensions)

    def is_valid(self, image_store_request: StoreImageGatewayRequest) -> bool:
        return image_store_request.image_extension in self.allowed_extensions
