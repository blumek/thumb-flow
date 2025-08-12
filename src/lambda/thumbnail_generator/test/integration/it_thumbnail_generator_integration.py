import base64
import json
import os
import uuid
from io import BytesIO
from typing import Dict, Any
from unittest import mock

import boto3
import pytest
from PIL import Image
from aws_lambda_typing.context import Context
from mypy_boto3_s3.client import S3Client
from mypy_boto3_s3.type_defs import GetObjectOutputTypeDef
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient

from dev_blumek_thumbnail_generator.bootstrap import application_bootstrap
from dev_blumek_thumbnail_generator.bootstrap.handler import (
    lambda_handler,
    generate_thumbnail,
)


class TestThumbnailGeneratorIntegration:
    @pytest.fixture
    def given_s3_client(self) -> S3Client:
        return boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
            endpoint_url=os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4567"),
        )

    @pytest.fixture
    def given_bedrock_client(self) -> BedrockRuntimeClient:
        mock_client: BedrockRuntimeClient = mock.Mock()
        mock_client.invoke_model.return_value = {
            "body": self.given_bedrock_response_body()
        }
        return mock_client

    def given_bedrock_response_body(self) -> mock.Mock:
        image_bytes: bytes = self.given_image_bytes(50, 50, "red")
        mock_body: mock.Mock = mock.Mock()
        mock_body.read.return_value = json.dumps(
            {"artifacts": [{"base64": base64.b64encode(image_bytes).decode("utf-8")}]}
        ).encode("utf-8")
        return mock_body

    @staticmethod
    def given_image_bytes(width: int, height: int, color: str) -> bytes:
        img: Image.Image = Image.new("RGB", (width, height), color=color)
        buffer: BytesIO = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue()

    @pytest.fixture
    def given_raw_bucket(self) -> str:
        bucket_name: str = os.environ.get(
            "AWS_S3_RAW_BUCKET_NAME", "thumbnail-generator-raw-bucket"
        )
        self.ensure_s3_bucket_exists(bucket_name)
        return bucket_name

    @pytest.fixture
    def given_thumbnail_bucket(self) -> str:
        bucket_name: str = os.environ.get(
            "AWS_S3_THUMBNAIL_BUCKET_NAME", "thumbnail-generator-thumbnail-bucket"
        )
        self.ensure_s3_bucket_exists(bucket_name)
        return bucket_name

    @staticmethod
    def ensure_s3_bucket_exists(bucket_name: str) -> None:
        s3_client: S3Client = boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
            endpoint_url=os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4567"),
        )
        try:
            s3_client.create_bucket(Bucket=bucket_name)
        except (
            s3_client.exceptions.BucketAlreadyOwnedByYou,
            s3_client.exceptions.BucketAlreadyExists,
        ):
            pass

    def test_generate_thumbnail_end_to_end(
        self,
        given_s3_client: S3Client,
        given_bedrock_client: BedrockRuntimeClient,
        given_raw_bucket: str,
        given_thumbnail_bucket: str,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        self.given_environment_variables(
            monkeypatch, given_raw_bucket, given_thumbnail_bucket
        )
        self.given_bedrock_client_is_available(given_bedrock_client)

        with self.given_s3_client_is_available(given_s3_client):
            image_key: str = self.given_image_is_uploaded(
                given_s3_client, given_raw_bucket
            )
            event: Dict[str, str] = self.given_valid_request(image_key)

            response: Dict[str, Any] = self.when_invoking_function(event)

            self.then_thumbnail_was_successfully_created(
                response, given_thumbnail_bucket, given_s3_client
            )

    @staticmethod
    def given_environment_variables(
        monkeypatch: pytest.MonkeyPatch,
        given_raw_bucket: str,
        given_thumbnail_bucket: str,
    ) -> None:
        monkeypatch.setenv("AWS_S3_RAW_BUCKET_NAME", given_raw_bucket)
        monkeypatch.setenv("AWS_S3_THUMBNAIL_BUCKET_NAME", given_thumbnail_bucket)
        monkeypatch.setenv(
            "AWS_ENDPOINT_URL",
            os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4567"),
        )

    @staticmethod
    def given_bedrock_client_is_available(
        given_bedrock_client: BedrockRuntimeClient,
    ) -> None:
        generate_thumbnail.thumbnail_generator._bedrock_client = given_bedrock_client

    @staticmethod
    def given_s3_client_is_available(given_s3_client: S3Client) -> mock.patch:
        return mock.patch.object(
            application_bootstrap, "s3_client", return_value=given_s3_client
        )

    def given_image_is_uploaded(
        self, given_s3_client: S3Client, bucket_name: str
    ) -> str:
        image_buffer: BytesIO = self.given_image_buffer(100, 100, "blue")
        image_name: str = f"test-image-{uuid.uuid4()}"
        test_image_key: str = f"{image_name}.png"
        given_s3_client.upload_fileobj(
            Fileobj=image_buffer,
            Bucket=bucket_name,
            Key=test_image_key,
            ExtraArgs={"ContentType": "image/png"},
        )
        return test_image_key

    @staticmethod
    def given_image_buffer(width: int, height: int, color: str) -> BytesIO:
        img: Image.Image = Image.new("RGB", (width, height), color=color)
        buffer: BytesIO = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    @staticmethod
    def given_valid_request(image_key: str) -> Dict[str, Any]:
        message_body = {
            "uploaded_image_key": image_key,
            "prompt": "Generate a thumbnail with red border",
        }
        return {"Records": [{"body": json.dumps(message_body)}]}

    def when_invoking_function(self, event: Dict[str, str]) -> Dict[str, Any]:
        lambda_context: Context = self.given_lambda_context()
        return lambda_handler(event, lambda_context)

    @staticmethod
    def given_lambda_context() -> Context:
        class MockLambdaContext(Context):
            function_name: str = "thumbnail_generator"
            memory_limit_in_mb: int = 128
            invoked_function_arn: str = (
                "arn:aws:lambda:us-east-1:123456789012:function:thumbnail_generator"
            )
            aws_request_id: str = str(uuid.uuid4())

        return MockLambdaContext()

    def then_thumbnail_was_successfully_created(
        self,
        response: Dict[str, Any],
        given_thumbnail_bucket: str,
        given_s3_client: S3Client,
    ) -> None:
        assert response["statusCode"] == 200
        assert "body" in response

        response_body = json.loads(response["body"])
        assert "responses" in response_body
        assert len(response_body["responses"]) > 0

        first_response = response_body["responses"][0]
        assert "image_key" in first_response

        thumbnail_key: str = first_response["image_key"]
        actual_thumbnail_bytes: bytes = self.given_image_from_s3(
            given_s3_client, given_thumbnail_bucket, thumbnail_key
        )
        expected_thumbnail_bytes: bytes = self.given_image_bytes(50, 50, "red")

        assert actual_thumbnail_bytes == expected_thumbnail_bytes

    @staticmethod
    def given_image_from_s3(given_s3_client: S3Client, bucket: str, key: str) -> bytes:
        response: GetObjectOutputTypeDef = given_s3_client.get_object(
            Bucket=bucket, Key=key
        )
        return response["Body"].read()

    def test_missing_required_field(
        self,
        given_raw_bucket: str,
        given_thumbnail_bucket: str,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        self.given_environment_variables(
            monkeypatch, given_raw_bucket, given_thumbnail_bucket
        )

        message_body: Dict[str, str] = {"uploaded_image_key": "given_image_key"}
        event: Dict[str, Any] = {"Records": [{"body": json.dumps(message_body)}]}
        response: Dict[str, Any] = self.when_invoking_function(event)

        assert response["statusCode"] == 207
        response_body = json.loads(response["body"])
        assert "responses" in response_body
        assert len(response_body["responses"]) == 1

        first_response = response_body["responses"][0]
        assert first_response["statusCode"] == 400
        assert "error" in first_response
        assert "Missing required field: 'prompt'" in first_response["error"]
        assert first_response["success"] is False
