import logging
from abc import ABC, abstractmethod

from infrastructure.repository.image_repository import ImageRepository
from infrastructure.repository.image_repository_model import StoreImageRequest
from infrastructure.gateway.image_persistence_gateway_model import (
    StoreImageGatewayRequest,
    StoreImageGatewayReply,
)
from infrastructure.policy.image_policy import ImagePolicy
from infrastructure.factory.image_key_factory import ImageKeyFactory

logger = logging.getLogger(__name__)


class ImagePersistenceGateway(ABC):
    @abstractmethod
    def store(self, request: StoreImageGatewayRequest) -> StoreImageGatewayReply:
        pass


class InvalidImageStoreRequestError(RuntimeError):
    pass


class S3ImagePersistenceGateway(ImagePersistenceGateway):
    def __init__(
        self,
        image_repository: ImageRepository,
        image_policy: ImagePolicy,
        image_key_factory: ImageKeyFactory,
    ):
        self.image_repository: ImageRepository = image_repository
        self.image_policy: ImagePolicy = image_policy
        self.image_key_factory: ImageKeyFactory = image_key_factory

    def store(self, request: StoreImageGatewayRequest) -> StoreImageGatewayReply:
        self.__validate_request(request)
        return self.__store(request)

    def __validate_request(self, request: StoreImageGatewayRequest) -> None:
        if not self.image_policy.is_valid(request):
            raise InvalidImageStoreRequestError(
                "Image store request does not comply with the policy"
            )

    def __store(self, request: StoreImageGatewayRequest) -> StoreImageGatewayReply:
        s3_key: str = self.image_key_factory.create_key(request.image_name)
        store_request = self.__to_store_image_request(request, s3_key)

        store_response = self.image_repository.store(store_request)
        logger.info(f"Image stored successfully with key: {store_response.image_key}")

        return StoreImageGatewayReply(image_key=store_response.image_key)

    @staticmethod
    def __to_store_image_request(request, s3_key):
        return StoreImageRequest(
            image_key=s3_key,
            image_extension=request.image_extension,
            image_bytes=request.image_bytes,
        )
