from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway_model import (
    StoreImageGatewayRequest,
)
from dev_blumek_upload_handler.infrastructure.policy.image_policy import ImagePolicy


class CompositeImagePolicy(ImagePolicy):
    def __init__(self, *policies: ImagePolicy):
        self.policies: tuple[ImagePolicy, ...] = policies

    def is_valid(self, image_store_request: StoreImageGatewayRequest) -> bool:
        for policy in self.policies:
            if not policy.is_valid(image_store_request):
                return False
        return True
