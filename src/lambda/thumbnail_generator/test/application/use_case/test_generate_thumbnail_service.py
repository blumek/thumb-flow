import unittest
from unittest.mock import Mock

from dev_blumek_thumbnail_generator.application.use_case.generate_thumbnail_service import (
    GenerateThumbnailService,
)
from dev_blumek_thumbnail_generator.application.use_case.generate_thumbail_use_case_model import (
    GenerateThumbnailUseCaseRequest,
    GenerateThumbnailUseCaseReply,
)
from dev_blumek_thumbnail_generator.domain.types.image_extension import ImageExtension
from dev_blumek_thumbnail_generator.infrastructure.gateway.image_persistence_gateway import (
    ImagePersistenceGateway,
)
from dev_blumek_thumbnail_generator.infrastructure.gateway.image_persistence_gateway_model import (
    StoreImageGatewayReply,
    StoreImageGatewayRequest,
)
from dev_blumek_thumbnail_generator.infrastructure.gateway.image_query_gateway import (
    ImageQueryGateway,
)
from dev_blumek_thumbnail_generator.infrastructure.gateway.image_query_gateway_model import (
    RetrieveImageGatewayReply,
    RetrieveImageGatewayRequest,
)
from dev_blumek_thumbnail_generator.infrastructure.generator.thumbnail_generator import (
    ThumbnailGenerator,
)
from dev_blumek_thumbnail_generator.infrastructure.generator.thumbnail_generator_model import (
    GenerateThumbnailRequest,
    GenerateThumbnailReply,
)


class TestGenerateThumbnailService(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_query_gateway: ImageQueryGateway = Mock(spec=ImageQueryGateway)
        self.image_persistence_gateway: ImagePersistenceGateway = Mock(
            spec=ImagePersistenceGateway
        )
        self.thumbnail_generator: ThumbnailGenerator = Mock(spec=ThumbnailGenerator)
        self.generate_thumbnail_service: GenerateThumbnailService = (
            GenerateThumbnailService(
                self.image_query_gateway,
                self.image_persistence_gateway,
                self.thumbnail_generator,
            )
        )

    def test_should_generate_thumbnail_successfully(self):
        self.given_image_can_be_retrieved()
        self.given_thumbnail_can_be_generated()
        self.given_thumbnail_can_be_stored()
        given_request: GenerateThumbnailUseCaseRequest = (
            self.given_generate_thumbnail_use_case_request()
        )

        actual_result: GenerateThumbnailUseCaseReply = (
            self.generate_thumbnail_service.generate_thumbnail(given_request)
        )

        self.assertEqual(actual_result, self.given_generate_thumbnail_use_case_reply())

    def given_image_can_be_retrieved(self):
        self.image_query_gateway.retrieve.return_value = (
            self.given_retrieve_image_gateway_reply()
        )

    def given_thumbnail_can_be_generated(self):
        self.thumbnail_generator.generate_thumbnail.return_value = (
            self.given_generate_thumbnail_reply()
        )

    def given_thumbnail_can_be_stored(self):
        self.image_persistence_gateway.store.return_value = (
            self.given_store_image_gateway_reply()
        )

    @staticmethod
    def given_retrieve_image_gateway_reply() -> RetrieveImageGatewayReply:
        return RetrieveImageGatewayReply(
            image_name="given_name",
            image_extension=ImageExtension.PNG,
            image_bytes=b"given_image_bytes",
        )

    @staticmethod
    def given_generate_thumbnail_reply() -> GenerateThumbnailReply:
        return GenerateThumbnailReply(thumbnail_bytes=b"given_thumbnail_bytes")

    @staticmethod
    def given_store_image_gateway_reply() -> StoreImageGatewayReply:
        return StoreImageGatewayReply(image_key="given_thumbnail_key")

    @staticmethod
    def given_generate_thumbnail_use_case_request() -> GenerateThumbnailUseCaseRequest:
        return GenerateThumbnailUseCaseRequest(
            image_key="given_image_key", prompt="given_prompt"
        )

    @staticmethod
    def given_generate_thumbnail_use_case_reply() -> GenerateThumbnailUseCaseReply:
        return GenerateThumbnailUseCaseReply(thumbnail_key="given_thumbnail_key")

    def test_should_call_the_underlying_query_gateway_to_retrieve_image(self):
        given_request: GenerateThumbnailUseCaseRequest = (
            self.given_generate_thumbnail_use_case_request()
        )

        self.generate_thumbnail_service.generate_thumbnail(given_request)

        self.image_query_gateway.retrieve.assert_called_once_with(
            self.given_expected_retrieve_image_gateway_request()
        )

    @staticmethod
    def given_expected_retrieve_image_gateway_request() -> RetrieveImageGatewayRequest:
        return RetrieveImageGatewayRequest(image_key="given_image_key")

    def test_should_call_the_underlying_thumbnail_generator_to_generate_thumbnail(self):
        self.given_image_can_be_retrieved()
        given_request: GenerateThumbnailUseCaseRequest = (
            self.given_generate_thumbnail_use_case_request()
        )

        self.generate_thumbnail_service.generate_thumbnail(given_request)

        self.thumbnail_generator.generate_thumbnail.assert_called_once_with(
            self.given_expected_generate_thumbnail_request()
        )

    @staticmethod
    def given_expected_generate_thumbnail_request() -> GenerateThumbnailRequest:
        return GenerateThumbnailRequest(
            input_image_bytes=b"given_image_bytes", prompt="given_prompt"
        )

    def test_should_call_the_underlying_persistence_gateway_to_store_thumbnail(self):
        self.given_image_can_be_retrieved()
        self.given_thumbnail_can_be_generated()
        given_request: GenerateThumbnailUseCaseRequest = (
            self.given_generate_thumbnail_use_case_request()
        )

        self.generate_thumbnail_service.generate_thumbnail(given_request)

        self.image_persistence_gateway.store.assert_called_once_with(
            self.given_expected_store_image_gateway_request()
        )

    @staticmethod
    def given_expected_store_image_gateway_request() -> StoreImageGatewayRequest:
        return StoreImageGatewayRequest(
            image_name="given_name",
            image_extension=ImageExtension.PNG,
            image_bytes=b"given_thumbnail_bytes",
        )


if __name__ == "__main__":
    unittest.main()
