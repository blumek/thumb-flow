import base64
import os
import uuid
from io import BytesIO

import boto3
import pytest
from PIL import Image
from aws_lambda_typing.context import Context

from dev_blumek_upload_handler.handler import lambda_handler


class TestImageUploadIntegration:
    @pytest.fixture
    def s3_client(self) -> boto3.client:
        return boto3.client(
            "s3",
            region_name=os.environ.get("AWS_REGION", "us-central-1"),
            endpoint_url=os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566"),
        )

    @pytest.fixture
    def s3_bucket(self) -> str:
        bucket_name: str = os.environ.get("AWS_S3_BUCKET_NAME", "test-bucket")
        s3: boto3.client = boto3.client(
            "s3",
            region_name=os.environ.get("AWS_REGION", "us-central-1"),
            endpoint_url=os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566"),
        )
        try:
            s3.create_bucket(Bucket=bucket_name)
        except s3.exceptions.BucketAlreadyOwnedByYou:
            pass
        except s3.exceptions.BucketAlreadyExists:
            pass

        return bucket_name

    def test_upload_image_end_to_end(self, s3_client, s3_bucket, monkeypatch):
        monkeypatch.setenv("AWS_S3_BUCKET_NAME", s3_bucket)

        given_event: dict[str, str] = self.given_request()

        actual_response: dict[str, str] = self.when_handling(given_event)

        self.then_process_passes_as_expected(actual_response, s3_bucket, s3_client)

    def given_request(self):
        event: dict[str, str] = {
            "image_name": "test_image",
            "image_extension": "png",
            "image_bytes": base64.b64encode(self.given_image_bytes()).decode("utf-8"),
        }
        return event

    @staticmethod
    def given_image_bytes():
        img = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def when_handling(self, given_event: dict[str, str]) -> dict[str, str]:
        given_lambda_context: Context = self.given_lambda_context()
        return lambda_handler(given_event, given_lambda_context)

    @staticmethod
    def given_lambda_context() -> Context:
        class MockLambdaContext(Context):
            function_name = "upload_handler"
            memory_limit_in_mb = 128
            invoked_function_arn = (
                "arn:aws:lambda:us-east-1:123456789012:function:upload_handler"
            )
            aws_request_id = str(uuid.uuid4())

        return MockLambdaContext()

    def then_process_passes_as_expected(
            self, actual_response: dict[str, str], s3_bucket: str, s3_client: boto3.client
    ):
        assert actual_response["statusCode"] == 200
        assert "image_key" in actual_response
        image_key = actual_response["image_key"]
        try:
            actual_s3_image_data = self.get_actual_s3_image_data(
                image_key, s3_bucket, s3_client
            )
            assert actual_s3_image_data == self.given_image_bytes()
        except s3_client.exceptions.NoSuchKey:
            pytest.fail(f"Image with key {image_key} was not found in S3")
        finally:
            s3_client.delete_object(Bucket=s3_bucket, Key=image_key)

    @staticmethod
    def get_actual_s3_image_data(image_key, s3_bucket, s3_client) -> bytes:
        s3_response = s3_client.get_object(Bucket=s3_bucket, Key=image_key)
        return s3_response["Body"].read()
