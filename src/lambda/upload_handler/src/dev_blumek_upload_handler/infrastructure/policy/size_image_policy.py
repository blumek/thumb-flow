from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway_model import (
    StoreImageGatewayRequest,
)
from dev_blumek_upload_handler.infrastructure.policy.image_policy import ImagePolicy


class SizeImagePolicy(ImagePolicy):
    def __init__(self, max_bytes_size: int):
        self.max_bytes_size: int = max_bytes_size

    def is_valid(self, image_store_request: StoreImageGatewayRequest) -> bool:
        return len(image_store_request.image_bytes) <= self.max_bytes_size
