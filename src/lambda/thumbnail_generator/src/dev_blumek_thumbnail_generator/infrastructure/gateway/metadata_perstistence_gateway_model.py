from dataclasses import dataclass


@dataclass(frozen=True)
class StoreMetadataGatewayRequest:
    workflow_id: str
    image_key: str


@dataclass(frozen=True)
class StoreMetadataGatewayReply:
    id: str
