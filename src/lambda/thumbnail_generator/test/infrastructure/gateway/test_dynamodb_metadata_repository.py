import unittest
from typing import Any
from unittest.mock import Mock

from dev_blumek_thumbnail_generator.infrastructure.gateway.dynamodb_metadata_persistence_gateway import (
    DynamoDBMetadataPersistenceGateway,
)
from dev_blumek_thumbnail_generator.infrastructure.gateway.metadata_perstistence_gateway_model import (
    StoreMetadataGatewayRequest,
    StoreMetadataGatewayReply,
)
from dev_blumek_thumbnail_generator.infrastructure.repository.metadata_repository import (
    MetadataRepository,
)
from dev_blumek_thumbnail_generator.infrastructure.repository.metadata_repository_model import (
    StoreMetadataRequest,
    StoreMetadataReply,
)


class TestDynamoDBMetadataPersistenceGateway(unittest.TestCase):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.metadata_repository: MetadataRepository = Mock(spec=MetadataRepository)
        self.dynamodb_metadata_persistence_gateway: (
            DynamoDBMetadataPersistenceGateway
        ) = DynamoDBMetadataPersistenceGateway(self.metadata_repository)

    def test_should_store_metadata_successfully_and_return_expected_result(
        self,
    ) -> None:
        self.given_metadata_can_be_stored()
        given_request: StoreMetadataGatewayRequest = (
            self.given_store_metadata_gateway_request()
        )

        actual_result: StoreMetadataGatewayReply = (
            self.dynamodb_metadata_persistence_gateway.store(given_request)
        )

        expected_result: StoreMetadataGatewayReply = (
            self.given_store_metadata_gateway_reply()
        )
        self.assertEqual(actual_result, expected_result)

    def given_metadata_can_be_stored(self) -> None:
        store_metadata_reply: StoreMetadataReply = self.given_store_metadata_reply()
        self.metadata_repository.store.return_value = store_metadata_reply

    @staticmethod
    def given_store_metadata_reply() -> StoreMetadataReply:
        return StoreMetadataReply(id="given_metadata_id")

    @staticmethod
    def given_store_metadata_gateway_request() -> StoreMetadataGatewayRequest:
        return StoreMetadataGatewayRequest(
            workflow_id="given_workflow_id", image_key="given_image_key"
        )

    @staticmethod
    def given_store_metadata_gateway_reply() -> StoreMetadataGatewayReply:
        return StoreMetadataGatewayReply(id="given_metadata_id")

    def test_should_call_metadata_repository_to_store_metadata(self) -> None:
        self.given_metadata_can_be_stored()
        given_request: StoreMetadataGatewayRequest = (
            self.given_store_metadata_gateway_request()
        )

        self.dynamodb_metadata_persistence_gateway.store(given_request)

        expected_request: StoreMetadataRequest = (
            self.given_expected_store_metadata_request()
        )
        self.metadata_repository.store.assert_called_once_with(expected_request)

    @staticmethod
    def given_expected_store_metadata_request() -> StoreMetadataRequest:
        return StoreMetadataRequest(
            workflow_id="given_workflow_id", image_key="given_image_key"
        )


if __name__ == "__main__":
    unittest.main()
