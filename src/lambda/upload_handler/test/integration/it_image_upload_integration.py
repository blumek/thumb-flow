import base64
import json
import os
import uuid
from io import BytesIO
from typing import Any, Dict, List, Tuple, cast

import boto3
import pytest
from PIL import Image
from aws_lambda_typing.context import Context
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table
from mypy_boto3_dynamodb.type_defs import (
    KeySchemaElementTypeDef,
    AttributeDefinitionTypeDef,
    ScanOutputTableTypeDef,
)
from mypy_boto3_s3.client import S3Client
from mypy_boto3_s3.type_defs import GetObjectOutputTypeDef
from mypy_boto3_sqs.client import SQSClient
from mypy_boto3_sqs.type_defs import (
    CreateQueueResultTypeDef,
    ReceiveMessageResultTypeDef,
)

from dev_blumek_upload_handler.bootstrap.handler import lambda_handler


class TestImageUploadIntegration:
    @pytest.fixture
    def s3_client(self) -> S3Client:
        return boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
            endpoint_url=os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566"),
        )

    @pytest.fixture
    def sqs_client(self) -> SQSClient:
        return boto3.client(
            "sqs",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
            endpoint_url=os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566"),
        )

    @pytest.fixture
    def s3_bucket(self) -> str:
        bucket_name: str = os.environ.get("AWS_S3_BUCKET_NAME", "test-bucket")
        s3: S3Client = boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
            endpoint_url=os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566"),
        )
        try:
            s3.create_bucket(Bucket=bucket_name)
        except s3.exceptions.BucketAlreadyOwnedByYou:
            pass
        except s3.exceptions.BucketAlreadyExists:
            pass

        return bucket_name

    @pytest.fixture
    def sqs_queue(self, sqs_client: SQSClient) -> str:
        queue_name: str = "upload-handler-test-queue"
        try:
            response: CreateQueueResultTypeDef = sqs_client.create_queue(
                QueueName=queue_name
            )
            return response["QueueUrl"]
        except Exception:
            return sqs_client.get_queue_url(QueueName=queue_name)["QueueUrl"]

    @pytest.fixture
    def dynamodb_table(self) -> Table:
        table_name: str = os.environ.get(
            "AWS_DYNAMODB_TABLE_NAME", "upload-handler-test-table"
        )
        dynamodb: DynamoDBServiceResource = boto3.resource(
            "dynamodb",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
            endpoint_url=os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566"),
        )

        key_schema: List[KeySchemaElementTypeDef] = [
            KeySchemaElementTypeDef(AttributeName="id", KeyType="HASH")
        ]

        attribute_definitions: List[AttributeDefinitionTypeDef] = [
            AttributeDefinitionTypeDef(AttributeName="id", AttributeType="S")
        ]

        try:
            table: Table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definitions,
                BillingMode="PAY_PER_REQUEST",
            )
            table.wait_until_exists()
        except Exception:
            table: Table = dynamodb.Table(table_name)

        return table

    def test_upload_image_end_to_end(
        self,
        s3_client: S3Client,
        s3_bucket: str,
        sqs_client: SQSClient,
        sqs_queue: str,
        dynamodb_table: Table,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("AWS_S3_BUCKET_NAME", s3_bucket)
        monkeypatch.setenv("AWS_SQS_QUEUE_URL", sqs_queue)
        monkeypatch.setenv("AWS_DYNAMODB_TABLE_NAME", dynamodb_table.name)
        monkeypatch.setenv("AWS_REGION", "us-east-1")
        monkeypatch.setenv("AWS_ENDPOINT_URL", "http://localhost:4566")
        given_event: Dict[str, str] = self.given_request()

        actual_response: Dict[str, str] = self.when_handling(given_event)

        self.then_process_passes_as_expected(
            actual_response, s3_bucket, s3_client, sqs_client, sqs_queue, dynamodb_table
        )

    def given_request(self) -> Dict[str, Any]:
        payload: Dict[str, str] = {
            "image_name": "test_image",
            "image_extension": "png",
            "image_bytes": base64.b64encode(self.given_image_bytes()).decode("utf-8"),
            "prompt": "Generate a thumbnail for this image",
        }

        return {
            "body": json.dumps(payload),
            "resource": "/{proxy+}",
            "path": "/upload",
            "httpMethod": "POST",
            "isBase64Encoded": False,
            "headers": {
                "Content-Type": "application/json",
                "Accept": "*/*",
            },
            "requestContext": {
                "resourcePath": "/{proxy+}",
                "httpMethod": "POST",
                "path": "/upload",
            },
        }

    @staticmethod
    def given_image_bytes() -> bytes:
        img: Image.Image = Image.new("RGB", (100, 100), color="red")
        buffer: BytesIO = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def when_handling(self, given_event: Dict[str, str]) -> Dict[str, str]:
        given_lambda_context: Context = self.given_lambda_context()
        return cast(Dict[str, str], lambda_handler(given_event, given_lambda_context))

    @staticmethod
    def given_lambda_context() -> Context:
        class MockLambdaContext(Context):
            function_name: str = "upload_handler"
            memory_limit_in_mb: int = 128
            invoked_function_arn: str = (
                "arn:aws:lambda:us-east-1:123456789012:function:upload_handler"
            )
            aws_request_id: str = str(uuid.uuid4())

        return MockLambdaContext()

    def then_process_passes_as_expected(
        self,
        actual_response: Dict[str, Any],
        s3_bucket: str,
        s3_client: S3Client,
        sqs_client: SQSClient,
        sqs_queue: str,
        dynamodb_table: Table,
    ) -> None:
        self.then_response_is_as_expected(actual_response)

        response_body: Dict[str, Any] = json.loads(actual_response["body"])
        image_key: str = response_body["image_key"]
        self.then_image_is_available_in_s3(image_key, s3_bucket, s3_client)
        self.then_sqs_message_emitted(image_key, sqs_client, sqs_queue)
        self.then_metadata_is_stored_in_dynamodb(image_key, dynamodb_table)

    @staticmethod
    def then_response_is_as_expected(actual_response: Dict[str, Any]) -> None:
        assert actual_response["statusCode"] == 200
        assert "body" in actual_response
        assert "headers" in actual_response
        assert actual_response["headers"].get("Content-Type") == "application/json"
        assert "image_key" in actual_response["body"]
        assert "workflow_id" in actual_response["body"]

    def then_image_is_available_in_s3(
        self, image_key: str, s3_bucket: str, s3_client: S3Client
    ) -> None:
        try:
            actual_s3_image_data: bytes = self.get_actual_s3_image_data(
                image_key, s3_bucket, s3_client
            )
            assert actual_s3_image_data == self.given_image_bytes()

        except s3_client.exceptions.NoSuchKey:
            pytest.fail(f"Image with key {image_key} was not found in S3")
        finally:
            s3_client.delete_object(Bucket=s3_bucket, Key=image_key)

    @staticmethod
    def get_actual_s3_image_data(
        image_key: str, s3_bucket: str, s3_client: S3Client
    ) -> bytes:
        s3_response: GetObjectOutputTypeDef = s3_client.get_object(
            Bucket=s3_bucket, Key=image_key
        )
        return s3_response["Body"].read()

    @staticmethod
    def then_sqs_message_emitted(
        image_key: str, sqs_client: SQSClient, queue_url: str
    ) -> None:
        response: ReceiveMessageResultTypeDef = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=1,
            MessageAttributeNames=["All"],
            VisibilityTimeout=1,
        )

        messages: List[Dict[str, Any]] = [
            json.loads(msg.get("Body", "{}")) for msg in response.get("Messages", [])
        ]
        matching_messages: List[Tuple[Dict[str, Any], str]] = [
            (msg, response["Messages"][index]["ReceiptHandle"])
            for index, msg in enumerate(messages)
            if msg.get("uploaded_image_key") == image_key
        ]

        if matching_messages:
            msg: Dict[str, Any]
            receipt: str
            msg, receipt = matching_messages[0]
            sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt)
            return

        assert (
            False
        ), f"No message with uploaded_image_key {image_key} found in SQS queue {queue_url}"

    @staticmethod
    def then_metadata_is_stored_in_dynamodb(
        image_key: str, dynamodb_table: Table
    ) -> None:
        response: ScanOutputTableTypeDef = dynamodb_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr("image_key").eq(image_key)
        )

        items: List[Dict[str, Any]] = response.get("Items", [])
        if not items:
            pytest.fail(
                f"No metadata record found in DynamoDB for image_key: {image_key}"
            )

        metadata_item: Dict[str, Any] = items[0]

        required_fields: set[str] = {"id", "workflow_id", "image_key", "image_name"}
        assert required_fields.issubset(
            metadata_item.keys()
        ), f"Metadata record should have all required fields: {required_fields}"

        assert (
            metadata_item["image_key"] == image_key
        ), f"Expected image_key '{image_key}', got '{metadata_item['image_key']}'"
        assert (
            metadata_item["image_name"] == "test_image"
        ), f"Expected image_name 'test_image', got '{metadata_item['image_name']}'"
        assert (
            metadata_item["image_extension"] == "png"
        ), f"Expected image_extension 'png', got '{metadata_item['image_extension']}'"
        assert (
            metadata_item["prompt"] == "Generate a thumbnail for this image"
        ), f"Expected prompt 'Generate a thumbnail for this image', got '{metadata_item['prompt']}'"

        assert (
            isinstance(metadata_item["id"], str) and len(metadata_item["id"]) > 0
        ), "ID should be a non-empty string"
        assert (
            isinstance(metadata_item["workflow_id"], str)
            and len(metadata_item["workflow_id"]) > 0
        ), "workflow_id should be a non-empty string"
