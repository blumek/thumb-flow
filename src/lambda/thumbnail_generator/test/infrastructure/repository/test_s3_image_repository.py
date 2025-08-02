import unittest
from unittest.mock import Mock, MagicMock
from typing import Any, Dict

from mypy_boto3_s3.client import S3Client
from botocore.exceptions import ClientError

from dev_blumek_thumbnail_generator.domain.types.image_extension import ImageExtension
from dev_blumek_thumbnail_generator.infrastructure.repository.image_repository_model import (
    StoreImageRequest,
    StoreImageReply,
    RetrieveImageRequest,
    RetrieveImageReply,
)
from dev_blumek_thumbnail_generator.infrastructure.repository.s3_image_repository import (
    S3ImageRepository,
    S3UploadError,
    S3RetrieveError,
)


class TestS3ImageRepository(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.s3_client: S3Client = Mock()
        self.s3_image_repository: S3ImageRepository = S3ImageRepository(
            s3_client=self.s3_client, bucket_name="given_bucket_name"
        )

    def test_should_store_image_successfully(self) -> None:
        self.given_s3_put_object_succeeds()
        given_request: StoreImageRequest = self.given_store_image_request()

        actual_result: StoreImageReply = self.s3_image_repository.store(given_request)

        self.assertEqual(actual_result, self.given_expected_store_image_reply())

    def given_s3_put_object_succeeds(self) -> None:
        self.s3_client.put_object.return_value = None

    @staticmethod
    def given_store_image_request() -> StoreImageRequest:
        return StoreImageRequest(
            image_key="given_image_key",
            image_extension=ImageExtension.PNG,
            image_bytes=b"given_image_bytes",
        )

    @staticmethod
    def given_expected_store_image_reply() -> StoreImageReply:
        return StoreImageReply(image_key="given_image_key")

    def test_should_call_the_underlying_s3_client_to_put_object(self) -> None:
        self.given_s3_put_object_succeeds()
        given_request: StoreImageRequest = self.given_store_image_request()

        self.s3_image_repository.store(given_request)

        self.s3_client.put_object.assert_called_once_with(
            Bucket="given_bucket_name",
            Key="given_image_key",
            Body=b"given_image_bytes",
            ContentType="image/png",
        )

    def test_should_raise_s3_upload_error_when_s3_client_fails(self) -> None:
        self.given_s3_put_object_fails()
        given_request: StoreImageRequest = self.given_store_image_request()

        with self.assertRaises(S3UploadError) as context:
            self.s3_image_repository.store(given_request)

        self.assertIn("Failed to store image: given_image_key", str(context.exception))

    def given_s3_put_object_fails(self) -> None:
        self.s3_client.put_object.side_effect = Exception("S3 connection error")

    def test_should_retrieve_image_successfully(self) -> None:
        self.given_s3_get_object_succeeds()
        given_request: RetrieveImageRequest = self.given_retrieve_image_request()

        actual_result: RetrieveImageReply = self.s3_image_repository.retrieve(
            given_request
        )

        self.assertEqual(actual_result, self.given_expected_retrieve_image_reply())

    def given_s3_get_object_succeeds(self) -> None:
        self.s3_client.get_object.return_value = self.given_s3_response()

    def given_s3_response(self) -> Dict[str, Any]:
        return {"Body": self.given_s3_response_body(), "ContentType": "image/png"}

    @staticmethod
    def given_s3_response_body() -> MagicMock:
        mock_body: MagicMock = MagicMock()
        mock_body.read.return_value = b"given_image_bytes"
        return mock_body

    @staticmethod
    def given_retrieve_image_request() -> RetrieveImageRequest:
        return RetrieveImageRequest(image_key="given_image_key")

    @staticmethod
    def given_expected_retrieve_image_reply() -> RetrieveImageReply:
        return RetrieveImageReply(
            image_name="given_image_key",
            image_extension=ImageExtension.PNG,
            image_bytes=b"given_image_bytes",
        )

    def test_should_call_the_underlying_s3_client_to_get_object(self) -> None:
        self.given_s3_get_object_succeeds()
        given_request: RetrieveImageRequest = self.given_retrieve_image_request()

        self.s3_image_repository.retrieve(given_request)

        self.s3_client.get_object.assert_called_once_with(
            Bucket="given_bucket_name",
            Key="given_image_key",
        )

    def test_should_raise_s3_retrieve_error_when_image_not_found(self) -> None:
        self.given_s3_get_object_raises_no_such_key_exception()
        given_request: RetrieveImageRequest = self.given_retrieve_image_request()

        with self.assertRaises(S3RetrieveError) as context:
            self.s3_image_repository.retrieve(given_request)

        self.assertIn(
            "Image under key: given_image_key not found", str(context.exception)
        )

    def given_s3_get_object_raises_no_such_key_exception(self) -> None:
        self.s3_client.exceptions.NoSuchKey = Exception
        self.s3_client.get_object.side_effect = self.s3_client.exceptions.NoSuchKey(
            "givenMessage"
        )

    def test_should_raise_s3_retrieve_error_when_s3_client_fails(self) -> None:
        self.given_s3_get_object_fails()
        given_request: RetrieveImageRequest = self.given_retrieve_image_request()

        with self.assertRaises(S3RetrieveError) as context:
            self.s3_image_repository.retrieve(given_request)

        self.assertIn(
            "Failed to retrieve image: given_image_key", str(context.exception)
        )

    def given_s3_get_object_fails(self) -> None:
        self.s3_client.exceptions = Mock()

        class NoSuchKey(ClientError):
            pass

        self.s3_client.exceptions.NoSuchKey = NoSuchKey
        self.s3_client.get_object.side_effect = Exception("givenMessage")


if __name__ == "__main__":
    unittest.main()
