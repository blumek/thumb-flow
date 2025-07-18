import unittest
from unittest.mock import Mock

from domain.types.image_extension import ImageExtension
from infrastructure.factory.image_key_factory import ImageKeyFactory
from infrastructure.gateway.image_persistence_gateway import (
    InvalidImageStoreRequestError,
)
from infrastructure.gateway.image_persistence_gateway_model import (
    StoreImageGatewayRequest,
    StoreImageGatewayReply,
)
from infrastructure.gateway.s3_image_persistence_gateway import (
    S3ImagePersistenceGateway,
)
from infrastructure.policy.image_policy import ImagePolicy
from infrastructure.repository.image_repository import ImageRepository
from infrastructure.repository.image_repository_model import (
    StoreImageRequest,
    StoreImageReply,
)


class TestS3ImagePersistenceGateway(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_repository: ImageRepository = Mock(spec=ImageRepository)
        self.image_policy: ImagePolicy = Mock(spec=ImagePolicy)
        self.image_key_factory: ImageKeyFactory = Mock(spec=ImageKeyFactory)
        self.s3_image_persistence_gateway: S3ImagePersistenceGateway = (
            S3ImagePersistenceGateway(
                self.image_repository, self.image_policy, self.image_key_factory
            )
        )

    def test_should_store_image_successfully(self):
        self.given_image_policy_is_valid()
        self.given_image_key_factory_creates_key()
        self.given_image_can_be_stored()
        given_request: StoreImageGatewayRequest = (
            self.given_store_image_gateway_request()
        )

        actual_result: StoreImageGatewayReply = self.s3_image_persistence_gateway.store(
            given_request
        )

        self.assertEqual(actual_result, self.given_store_image_gateway_reply())

    def given_image_policy_is_valid(self):
        self.image_policy.is_valid.return_value = True

    def given_image_key_factory_creates_key(self):
        self.image_key_factory.create_key.return_value = "given_s3_key"

    def given_image_can_be_stored(self):
        self.image_repository.store.return_value = self.given_store_image_reply()

    @staticmethod
    def given_store_image_reply() -> StoreImageReply:
        return StoreImageReply(image_key="given_s3_key")

    @staticmethod
    def given_store_image_gateway_request() -> StoreImageGatewayRequest:
        return StoreImageGatewayRequest(
            image_name="given_image_name",
            image_extension=ImageExtension.PNG,
            image_bytes=b"given_image_bytes",
        )

    @staticmethod
    def given_store_image_gateway_reply() -> StoreImageGatewayReply:
        return StoreImageGatewayReply(image_key="given_s3_key")

    def test_should_call_image_policy_to_validate_request(self):
        self.given_image_policy_is_valid()
        self.given_image_key_factory_creates_key()
        self.given_image_can_be_stored()
        given_request: StoreImageGatewayRequest = (
            self.given_store_image_gateway_request()
        )

        self.s3_image_persistence_gateway.store(given_request)

        self.image_policy.is_valid.assert_called_once_with(given_request)

    def test_should_call_image_key_factory_to_create_key(self):
        self.given_image_policy_is_valid()
        self.given_image_key_factory_creates_key()
        self.given_image_can_be_stored()
        given_request: StoreImageGatewayRequest = (
            self.given_store_image_gateway_request()
        )

        self.s3_image_persistence_gateway.store(given_request)

        self.image_key_factory.create_key.assert_called_once_with("given_image_name")

    def test_should_call_image_repository_to_store_image(self):
        self.given_image_policy_is_valid()
        self.given_image_key_factory_creates_key()
        self.given_image_can_be_stored()
        given_request: StoreImageGatewayRequest = (
            self.given_store_image_gateway_request()
        )

        self.s3_image_persistence_gateway.store(given_request)

        self.image_repository.store.assert_called_once_with(
            self.given_expected_store_image_request()
        )

    @staticmethod
    def given_expected_store_image_request() -> StoreImageRequest:
        return StoreImageRequest(
            image_key="given_s3_key",
            image_extension=ImageExtension.PNG,
            image_bytes=b"given_image_bytes",
        )

    def test_should_raise_error_when_policy_validation_fails(self):
        self.given_image_policy_is_not_valid()
        given_request: StoreImageGatewayRequest = (
            self.given_store_image_gateway_request()
        )

        with self.assertRaises(InvalidImageStoreRequestError) as context:
            self.s3_image_persistence_gateway.store(given_request)

        self.assertEqual(
            str(context.exception),
            "Image store request does not comply with the policy",
        )

    def given_image_policy_is_not_valid(self):
        self.image_policy.is_valid.return_value = False

    def test_should_not_call_repository_when_policy_validation_fails(self):
        self.given_image_policy_is_not_valid()
        given_request: StoreImageGatewayRequest = (
            self.given_store_image_gateway_request()
        )

        with self.assertRaises(InvalidImageStoreRequestError):
            self.s3_image_persistence_gateway.store(given_request)

        self.image_repository.store.assert_not_called()


if __name__ == "__main__":
    unittest.main()
