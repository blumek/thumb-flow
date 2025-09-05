from typing import Dict

from mypy_boto3_dynamodb.service_resource import Table
from mypy_boto3_dynamodb.type_defs import TableAttributeValueTypeDef

from dev_blumek_thumbnail_generator.infrastructure.factory.metadata_identifier_factory import (
    MetadataIdentifierFactory,
)
from dev_blumek_thumbnail_generator.infrastructure.repository.metadata_repository import (
    MetadataRepository,
)
from dev_blumek_thumbnail_generator.infrastructure.repository.metadata_repository_model import (
    StoreMetadataRequest,
    StoreMetadataReply,
)


class DynamoDBMetadataRepository(MetadataRepository):
    def __init__(
        self, table: Table, metadata_identifier_factory: MetadataIdentifierFactory
    ):
        self.table = table
        self.metadata_identifier_factory = metadata_identifier_factory

    def store(self, store_metadata_request: StoreMetadataRequest) -> StoreMetadataReply:
        identifier: str = self.metadata_identifier_factory.create_identifier()
        item: Dict[str, TableAttributeValueTypeDef] = self.__to_dynamodb_item(
            identifier, store_metadata_request
        )
        self.table.put_item(Item=item)
        return StoreMetadataReply(id=identifier)

    @staticmethod
    def __to_dynamodb_item(
        identifier: str, store_metadata_request: StoreMetadataRequest
    ) -> Dict[str, TableAttributeValueTypeDef]:
        return {
            "id": identifier,
            "workflow_id": store_metadata_request.workflow_id,
            "image_key": store_metadata_request.image_key,
        }
