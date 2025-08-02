import unittest
from unittest.mock import Mock

from dev_blumek_thumbnail_generator.domain.types.image_extension import ImageExtension
from dev_blumek_thumbnail_generator.infrastructure.gateway.image_query_gateway_model import (
    RetrieveImageGatewayRequest,
    RetrieveImageGatewayReply,
)
from dev_blumek_thumbnail_generator.infrastructure.gateway.s3_image_query_gateway import (
    S3ImageQueryGateway,
)
from dev_blumek_thumbnail_generator.infrastructure.repository.image_repository import (
    ImageRepository,
)
from dev_blumek_thumbnail_generator.infrastructure.repository.image_repository_model import (
    RetrieveImageReply,
    RetrieveImageRequest,
)


class TestS3ImageQueryGateway(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_repository: ImageRepository = Mock(spec=ImageRepository)
        self.s3_image_query_gateway: S3ImageQueryGateway = S3ImageQueryGateway(
            self.image_repository
        )

    def test_should_retrieve_image_successfully(self):
        self.given_image_can_be_retrieved()
        given_request: RetrieveImageGatewayRequest = (
            self.given_retrieve_image_gateway_request()
        )

        actual_result: RetrieveImageGatewayReply = self.s3_image_query_gateway.retrieve(
            given_request
        )

        self.assertEqual(actual_result, self.given_retrieve_image_gateway_reply())

    def given_image_can_be_retrieved(self):
        self.image_repository.retrieve.return_value = self.given_retrieve_image_reply()

    @staticmethod
    def given_retrieve_image_reply() -> RetrieveImageReply:
        return RetrieveImageReply(
            image_name="given_image_name",
            image_extension=ImageExtension.PNG,
            image_bytes=b"given_image_bytes",
        )

    @staticmethod
    def given_retrieve_image_gateway_request() -> RetrieveImageGatewayRequest:
        return RetrieveImageGatewayRequest(image_key="given_image_key")

    @staticmethod
    def given_retrieve_image_gateway_reply() -> RetrieveImageGatewayReply:
        return RetrieveImageGatewayReply(
            image_name="given_image_name",
            image_extension=ImageExtension.PNG,
            image_bytes=b"given_image_bytes",
        )

    def test_should_call_image_repository_to_retrieve_image(self):
        self.given_image_can_be_retrieved()
        given_request: RetrieveImageGatewayRequest = (
            self.given_retrieve_image_gateway_request()
        )

        self.s3_image_query_gateway.retrieve(given_request)

        self.image_repository.retrieve.assert_called_once_with(
            self.given_expected_retrieve_image_request()
        )

    @staticmethod
    def given_expected_retrieve_image_request() -> RetrieveImageRequest:
        return RetrieveImageRequest(image_key="given_image_key")


if __name__ == "__main__":
    unittest.main()
