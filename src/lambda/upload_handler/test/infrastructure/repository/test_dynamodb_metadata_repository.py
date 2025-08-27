import unittest
from typing import Dict, Any
from unittest.mock import Mock

from dev_blumek_upload_handler.domain.types.image_extension import ImageExtension
from dev_blumek_upload_handler.infrastructure.factory.metadata_identifier_factory import (
    MetadataIdentifierFactory,
)
from dev_blumek_upload_handler.infrastructure.repository.dynamodb_metadata_repository import (
    DynamoDBMetadataRepository,
)
from dev_blumek_upload_handler.infrastructure.repository.metadata_repository_model import (
    StoreMetadataRequest,
    StoreMetadataReply,
)


class TestDynamoDBMetadataRepository(unittest.TestCase):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.table: Mock = Mock()
        self.metadata_identifier_factory: MetadataIdentifierFactory = Mock(
            spec=MetadataIdentifierFactory
        )
        self.dynamodb_metadata_repository: DynamoDBMetadataRepository = (
            DynamoDBMetadataRepository(
                table=self.table,
                metadata_identifier_factory=self.metadata_identifier_factory,
            )
        )

    def test_should_store_metadata_successfully(self) -> None:
        self.given_metadata_identifier_factory_creates_identifier()
        self.given_table_put_item_succeeds()
        given_request: StoreMetadataRequest = self.given_store_metadata_request()

        actual_result: StoreMetadataReply = self.dynamodb_metadata_repository.store(
            given_request
        )

        self.assertEqual(actual_result, self.given_expected_store_metadata_reply())

    def given_metadata_identifier_factory_creates_identifier(self) -> None:
        self.metadata_identifier_factory.create_identifier.return_value = (
            "given_identifier"
        )

    def given_table_put_item_succeeds(self) -> None:
        self.table.put_item.return_value = None

    @staticmethod
    def given_store_metadata_request() -> StoreMetadataRequest:
        return StoreMetadataRequest(
            workflow_id="given_workflow_id",
            image_key="given_image_key",
            image_name="given_image_name",
            image_extension=ImageExtension.PNG,
            prompt="given_prompt",
        )

    @staticmethod
    def given_expected_store_metadata_reply() -> StoreMetadataReply:
        return StoreMetadataReply(id="given_identifier")

    def test_should_call_metadata_identifier_factory_to_create_identifier(self) -> None:
        self.given_metadata_identifier_factory_creates_identifier()
        self.given_table_put_item_succeeds()
        given_request: StoreMetadataRequest = self.given_store_metadata_request()

        self.dynamodb_metadata_repository.store(given_request)

        self.metadata_identifier_factory.create_identifier.assert_called_once()

    def test_should_call_table_to_put_item_with_correct_data(self) -> None:
        self.given_metadata_identifier_factory_creates_identifier()
        self.given_table_put_item_succeeds()
        given_request: StoreMetadataRequest = self.given_store_metadata_request()

        self.dynamodb_metadata_repository.store(given_request)

        self.table.put_item.assert_called_once_with(
            Item=self.given_expected_dynamodb_item()
        )

    @staticmethod
    def given_expected_dynamodb_item() -> Dict[str, Any]:
        return {
            "id": "given_identifier",
            "workflow_id": "given_workflow_id",
            "image_key": "given_image_key",
            "image_name": "given_image_name",
            "image_extension": "png",
            "prompt": "given_prompt",
        }


if __name__ == "__main__":
    unittest.main()
