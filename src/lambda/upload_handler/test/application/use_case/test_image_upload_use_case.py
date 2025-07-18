import unittest
from unittest.mock import Mock

from dev_blumek_upload_handler.application.use_case.image_upload_service import (
    UploadImageService,
)
from dev_blumek_upload_handler.application.use_case.image_upload_use_case_model import (
    StoreImageUseCaseRequest,
    StoreImageUseCaseReply,
)
from dev_blumek_upload_handler.domain.types.image_extension import ImageExtension
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway import (
    ImagePersistenceGateway,
)
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway_model import (
    StoreImageGatewayReply,
    StoreImageGatewayRequest,
)


class TestImageUploadUseCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_persistence_gateway: ImagePersistenceGateway = Mock(
            spec=ImagePersistenceGateway
        )
        self.upload_image_service: UploadImageService = UploadImageService(
            self.image_persistence_gateway
        )

    def test_should_upload_image_successfully(self):
        self.given_image_can_be_stored()
        given_request: StoreImageUseCaseRequest = (
            self.given_store_image_use_case_request()
        )

        actual_result: StoreImageUseCaseReply = self.upload_image_service.upload_image(
            given_request
        )

        self.assertEqual(actual_result, self.given_store_image_use_case_reply())

    def given_image_can_be_stored(self):
        self.image_persistence_gateway.store.return_value = (
            self.given_store_image_gateway_reply()
        )

    @staticmethod
    def given_store_image_gateway_reply() -> StoreImageGatewayReply:
        return StoreImageGatewayReply(image_key="given_image_key")

    @staticmethod
    def given_store_image_use_case_request() -> StoreImageUseCaseRequest:
        return StoreImageUseCaseRequest(
            image_name="given_name",
            image_extension=ImageExtension.PNG,
            image_bytes=b"given_image_bytes",
        )

    @staticmethod
    def given_store_image_use_case_reply() -> StoreImageUseCaseReply:
        return StoreImageUseCaseReply(image_key="given_image_key")

    def test_should_call_the_underlying_gateway_to_store_image(self):
        given_request: StoreImageUseCaseRequest = (
            self.given_store_image_use_case_request()
        )

        self.upload_image_service.upload_image(given_request)

        self.image_persistence_gateway.store.assert_called_once_with(
            self.given_expected_store_image_gateway_request()
        )

    @staticmethod
    def given_expected_store_image_gateway_request() -> StoreImageGatewayRequest:
        return StoreImageGatewayRequest(
            image_name="given_name",
            image_extension=ImageExtension.PNG,
            image_bytes=b"given_image_bytes",
        )


if __name__ == "__main__":
    unittest.main()
