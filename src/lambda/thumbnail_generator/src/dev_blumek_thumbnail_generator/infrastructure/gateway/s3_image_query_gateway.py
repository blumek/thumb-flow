from dev_blumek_thumbnail_generator.infrastructure.gateway.image_query_gateway import (
    ImageQueryGateway,
)
from dev_blumek_thumbnail_generator.infrastructure.gateway.image_query_gateway_model import (
    RetrieveImageGatewayRequest,
    RetrieveImageGatewayReply,
)
from dev_blumek_thumbnail_generator.infrastructure.repository.image_repository import (
    ImageRepository,
)
from dev_blumek_thumbnail_generator.infrastructure.repository.image_repository_model import (
    RetrieveImageRequest,
    RetrieveImageReply,
)


class S3ImageQueryGateway(ImageQueryGateway):
    def __init__(self, image_repository: ImageRepository):
        self.image_repository: ImageRepository = image_repository

    def retrieve(
        self, request: RetrieveImageGatewayRequest
    ) -> RetrieveImageGatewayReply:
        retrieve_request: RetrieveImageRequest = self.__to_retrieve_image_request(
            request
        )
        retrieve_response: RetrieveImageReply = self.image_repository.retrieve(
            retrieve_request
        )
        return self.__to_retrieve_image_gateway_reply(retrieve_response)

    @staticmethod
    def __to_retrieve_image_request(
        request: RetrieveImageGatewayRequest,
    ) -> RetrieveImageRequest:
        return RetrieveImageRequest(image_key=request.image_key)

    @staticmethod
    def __to_retrieve_image_gateway_reply(
        retrieve_response: RetrieveImageReply,
    ) -> RetrieveImageGatewayReply:
        return RetrieveImageGatewayReply(
            image_name=retrieve_response.image_name,
            image_bytes=retrieve_response.image_bytes,
            image_extension=retrieve_response.image_extension,
        )
