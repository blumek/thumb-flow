from abc import ABC, abstractmethod
from infrastructure.gateway.image_persistence_gateway_model import StoreImageGatewayRequest


class ImagePolicy(ABC):
    @abstractmethod
    def is_valid(self, image_store_request: StoreImageGatewayRequest) -> bool:
        pass


class ImagePolicyComposite(ImagePolicy):
    def __init__(self, *policies: ImagePolicy):
        self.policies: tuple[ImagePolicy, ...] = policies

    def is_valid(self, image_store_request: StoreImageGatewayRequest) -> bool:
        for policy in self.policies:
            if not policy.is_valid(image_store_request):
                return False
        return True


class ImagePolicySize(ImagePolicy):
    def __init__(self, max_bytes_size: int):
        self.max_bytes_size: int = max_bytes_size

    def is_valid(self, image_store_request: StoreImageGatewayRequest) -> bool:
        return len(image_store_request.image_bytes) <= self.max_bytes_size


class ImagePolicyExtension(ImagePolicy):
    def __init__(self, allowed_extensions: set[str]):
        self.allowed_extensions: set[str] = {extension.lower() for extension in allowed_extensions}

    def is_valid(self, image_store_request: StoreImageGatewayRequest) -> bool:
        return image_store_request.image_extension.value.lower() in self.allowed_extensions
