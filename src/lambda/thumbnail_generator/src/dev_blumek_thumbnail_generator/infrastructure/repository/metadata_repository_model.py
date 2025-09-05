from dataclasses import dataclass


@dataclass(frozen=True)
class StoreMetadataRequest:
    workflow_id: str
    image_key: str


@dataclass(frozen=True)
class StoreMetadataReply:
    id: str
