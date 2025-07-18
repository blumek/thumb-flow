import unittest
from unittest.mock import Mock

from dev_blumek_upload_handler.domain.types.image_extension import ImageExtension
from dev_blumek_upload_handler.infrastructure.repository.image_repository_model import (
    StoreImageRequest,
    StoreImageReply,
)
from dev_blumek_upload_handler.infrastructure.repository.s3_image_repository import (
    S3ImageRepository,
    S3UploadError,
)


class TestS3ImageRepository(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.s3_client = Mock()
        self.bucket_name: str = "given_bucket_name"
        self.s3_image_repository = S3ImageRepository(
            s3_client=self.s3_client, bucket_name=self.bucket_name
        )

    def test_should_store_image_successfully(self):
        self.given_s3_put_object_succeeds()
        given_request: StoreImageRequest = self.given_store_image_request()

        actual_result: StoreImageReply = self.s3_image_repository.store(given_request)

        self.assertEqual(actual_result, self.given_expected_store_image_reply())

    def given_s3_put_object_succeeds(self):
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

    def test_should_call_the_underlying_s3_client_to_put_object(self):
        self.given_s3_put_object_succeeds()
        given_request: StoreImageRequest = self.given_store_image_request()

        self.s3_image_repository.store(given_request)

        self.s3_client.put_object.assert_called_once_with(
            Bucket=self.bucket_name,
            Key="given_image_key",
            Body=b"given_image_bytes",
            ContentType="image/png",
        )

    def test_should_raise_s3_upload_error_when_s3_client_fails(self):
        self.given_s3_put_object_fails()
        given_request: StoreImageRequest = self.given_store_image_request()

        with self.assertRaises(S3UploadError) as context:
            self.s3_image_repository.store(given_request)

        self.assertIn("Failed to store image: given_image_key", str(context.exception))

    def given_s3_put_object_fails(self):
        self.s3_client.put_object.side_effect = Exception("S3 connection error")


if __name__ == "__main__":
    unittest.main()
