import unittest
from unittest.mock import Mock

from dev_blumek_upload_handler.application.use_case.initialize_thumbnail_generation_service import (
    InitializeThumbnailGenerationService,
)
from dev_blumek_upload_handler.application.use_case.initialize_thumbnail_generation_use_case_model import (
    InitializeThumbnailGenerationUseCaseRequest,
    InitializeThumbnailGenerationUseCaseReply,
)
from dev_blumek_upload_handler.domain.types.image_extension import ImageExtension
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway import (
    ImagePersistenceGateway,
)
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway_model import (
    StoreImageGatewayReply,
    StoreImageGatewayRequest,
)
from dev_blumek_upload_handler.infrastructure.messaging.event_publisher import (
    EventPublisher,
)
from dev_blumek_upload_handler.infrastructure.messaging.thumbnail_generation_requested_event import (
    ThumbnailGenerationRequestedEvent,
)


class TestInitializeThumbnailGenerationUseCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_persistence_gateway: ImagePersistenceGateway = Mock(
            spec=ImagePersistenceGateway
        )
        self.event_publisher: EventPublisher = Mock()
        self.upload_image_service: InitializeThumbnailGenerationService = (
            InitializeThumbnailGenerationService(
                self.image_persistence_gateway, self.event_publisher
            )
        )

    def test_should_upload_image_successfully(self):
        self.given_image_can_be_stored()
        given_request: InitializeThumbnailGenerationUseCaseRequest = (
            self.given_store_image_use_case_request()
        )

        actual_result: InitializeThumbnailGenerationUseCaseReply = (
            self.upload_image_service.upload_image(given_request)
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
    def given_store_image_use_case_request() -> (
        InitializeThumbnailGenerationUseCaseRequest
    ):
        return InitializeThumbnailGenerationUseCaseRequest(
            image_name="given_name",
            image_extension=ImageExtension.PNG,
            image_bytes=b"given_image_bytes",
            prompt="given_prompt",
        )

    @staticmethod
    def given_store_image_use_case_reply() -> InitializeThumbnailGenerationUseCaseReply:
        return InitializeThumbnailGenerationUseCaseReply(image_key="given_image_key")

    def test_should_call_the_underlying_gateway_to_store_image(self):
        given_request: InitializeThumbnailGenerationUseCaseRequest = (
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

    def test_should_call_the_underlying_event_publisher(self):
        self.given_image_can_be_stored()

        given_request: InitializeThumbnailGenerationUseCaseRequest = (
            self.given_store_image_use_case_request()
        )

        self.upload_image_service.upload_image(given_request)

        self.event_publisher.publish.assert_called_once()
        self.event_publisher.publish.assert_called_with(self.given_event())

    @staticmethod
    def given_event() -> ThumbnailGenerationRequestedEvent:
        return ThumbnailGenerationRequestedEvent(
            uploaded_image_key="given_image_key",
            prompt="given_prompt",
        )


if __name__ == "__main__":
    unittest.main()
