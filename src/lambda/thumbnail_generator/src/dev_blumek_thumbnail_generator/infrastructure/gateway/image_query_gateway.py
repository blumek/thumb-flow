from abc import ABC

from dev_blumek_thumbnail_generator.infrastructure.gateway.image_query_gateway_model import (
    RetrieveImageGatewayRequest,
    RetrieveImageGatewayReply,
)


class ImageQueryGateway(ABC):
    def retrieve(
        self, request: RetrieveImageGatewayRequest
    ) -> RetrieveImageGatewayReply:
        pass
