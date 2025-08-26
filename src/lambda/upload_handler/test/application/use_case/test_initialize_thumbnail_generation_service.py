import unittest
from typing import Any
from unittest.mock import Mock

from dev_blumek_upload_handler.application.use_case.initialize_thumbnail_generation_service import (
    InitializeThumbnailGenerationService,
)
from dev_blumek_upload_handler.application.use_case.initialize_thumbnail_generation_use_case_model import (
    InitializeThumbnailGenerationUseCaseRequest,
    InitializeThumbnailGenerationUseCaseReply,
)
from dev_blumek_upload_handler.domain.types.image_extension import ImageExtension
from dev_blumek_upload_handler.infrastructure.factory.thumbnail_generation_identifier_factory import (
    WorkflowIdentifierFactory,
)
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway import (
    ImagePersistenceGateway,
)
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway_model import (
    StoreImageGatewayReply,
    StoreImageGatewayRequest,
)
from dev_blumek_upload_handler.infrastructure.gateway.metadata_persistence_gateway import (
    MetadataPersistenceGateway,
)
from dev_blumek_upload_handler.infrastructure.gateway.metadata_perstistence_gateway_model import (
    StoreMetadataGatewayReply,
    StoreMetadataGatewayRequest,
)
from dev_blumek_upload_handler.infrastructure.messaging.event_publisher import (
    EventPublisher,
)
from dev_blumek_upload_handler.infrastructure.messaging.thumbnail_generation_requested_event import (
    ThumbnailGenerationRequestedEvent,
)


class TestInitializeThumbnailGenerationUseCase(unittest.TestCase):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.workflow_identifier_factory: WorkflowIdentifierFactory = Mock()
        self.image_persistence_gateway: ImagePersistenceGateway = Mock(
            spec=ImagePersistenceGateway
        )
        self.metadata_persistence_gateway: MetadataPersistenceGateway = Mock()
        self.event_publisher: EventPublisher = Mock()
        self.upload_image_service: InitializeThumbnailGenerationService = (
            InitializeThumbnailGenerationService(
                workflow_identifier_factory=self.workflow_identifier_factory,
                image_persistence_gateway=self.image_persistence_gateway,
                metadata_persistence_gateway=self.metadata_persistence_gateway,
                event_publisher=self.event_publisher,
            )
        )

    def test_should_upload_image_successfully(self) -> None:
        self.given_workflow_id_can_be_created()
        self.given_image_can_be_stored()
        given_request: InitializeThumbnailGenerationUseCaseRequest = (
            self.given_store_image_use_case_request()
        )

        actual_result: InitializeThumbnailGenerationUseCaseReply = (
            self.upload_image_service.upload_image(given_request)
        )

        self.assertEqual(actual_result, self.given_store_image_use_case_reply())

    def given_image_can_be_stored(self) -> None:
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
        return InitializeThumbnailGenerationUseCaseReply(
            workflow_id="given_workflow_id", image_key="given_image_key"
        )

    def test_should_call_the_underlying_factory_to_create_workflow_id(self) -> None:
        self.given_workflow_id_can_be_created()
        given_request: InitializeThumbnailGenerationUseCaseRequest = (
            self.given_store_image_use_case_request()
        )

        self.upload_image_service.upload_image(given_request)

        self.workflow_identifier_factory.create_identifier.assert_called_once()

    def given_workflow_id_can_be_created(self) -> None:
        self.workflow_identifier_factory.create_identifier.return_value = (
            "given_workflow_id"
        )

    def test_should_call_the_underlying_gateway_to_store_image(self) -> None:
        self.given_workflow_id_can_be_created()
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
            workflow_id="given_workflow_id",
            image_name="given_name",
            image_extension=ImageExtension.PNG,
            image_bytes=b"given_image_bytes",
        )

    def test_should_call_the_underlying_gateway_to_store_metadata(self) -> None:
        self.given_workflow_id_can_be_created()
        self.given_image_can_be_stored()
        self.given_metadata_can_be_stored()
        given_request: InitializeThumbnailGenerationUseCaseRequest = (
            self.given_store_image_use_case_request()
        )

        self.upload_image_service.upload_image(given_request)

        self.metadata_persistence_gateway.store.assert_called_once_with(
            self.given_expected_store_metadata_gateway_request()
        )

    def given_metadata_can_be_stored(self) -> None:
        self.metadata_persistence_gateway.store.return_value = (
            StoreMetadataGatewayReply(id="given_metadata_id")
        )

    @staticmethod
    def given_expected_store_metadata_gateway_request() -> StoreMetadataGatewayRequest:
        return StoreMetadataGatewayRequest(
            image_key="given_image_key",
            image_name="given_name",
            image_extension=ImageExtension.PNG,
            prompt="given_prompt",
            workflow_id="given_workflow_id",
        )

    def test_should_call_the_underlying_event_publisher(self) -> None:
        self.given_workflow_id_can_be_created()
        self.given_image_can_be_stored()
        given_request: InitializeThumbnailGenerationUseCaseRequest = (
            self.given_store_image_use_case_request()
        )

        self.upload_image_service.upload_image(given_request)

        self.event_publisher.publish.assert_called_with(self.given_event())

    @staticmethod
    def given_event() -> ThumbnailGenerationRequestedEvent:
        return ThumbnailGenerationRequestedEvent(
            workflow_id="given_workflow_id",
            uploaded_image_key="given_image_key",
            prompt="given_prompt",
        )


if __name__ == "__main__":
    unittest.main()
