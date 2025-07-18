from dev_blumek_upload_handler.domain.types.image_extension import ImageExtension
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway_model import (
    StoreImageGatewayRequest,
)
from dev_blumek_upload_handler.infrastructure.policy.image_policy import ImagePolicy


class ExtensionImagePolicy(ImagePolicy):
    def __init__(self, allowed_extensions: set[ImageExtension]):
        self.allowed_extensions: set[ImageExtension] = set(allowed_extensions)

    def is_valid(self, image_store_request: StoreImageGatewayRequest) -> bool:
        return image_store_request.image_extension in self.allowed_extensions
