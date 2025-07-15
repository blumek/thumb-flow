import base64
from typing import Dict, Any

from aws_lambda_typing.context import Context as LambdaContext

from application_bootstrap import upload_image_use_case
from image_extension import ImageExtension
from image_upload_use_case_model import StoreImageUseCaseRequest, StoreImageUseCaseReply

upload_image = upload_image_use_case()


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    store_image_request: StoreImageUseCaseRequest = __to_store_image_request(event)
    store_image_reply: StoreImageUseCaseReply = upload_image.upload_image(store_image_request)
    return {
        "statusCode": 200,
        "image_key": store_image_reply.image_key,
    }


def __to_store_image_request(event: Dict[str, Any]) -> StoreImageUseCaseRequest:
    return StoreImageUseCaseRequest(
        image_name=event['image_name'],
        image_extension=ImageExtension(event['image_extension']),
        image_bytes=base64.b64decode(event['image_bytes'])
    )
