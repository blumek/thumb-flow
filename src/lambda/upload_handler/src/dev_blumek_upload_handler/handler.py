import base64
import logging
from typing import Dict, Any

from aws_lambda_typing.context import Context as LambdaContext

from dev_blumek_upload_handler.application_bootstrap import upload_image_use_case
from dev_blumek_upload_handler.domain.types.image_extension import ImageExtension
from dev_blumek_upload_handler.application.use_case.image_upload_use_case_model import (
    StoreImageUseCaseRequest,
    StoreImageUseCaseReply,
)

upload_image = upload_image_use_case()
logger = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    try:
        store_image_request: StoreImageUseCaseRequest = __to_store_image_request(event)
        store_image_reply: StoreImageUseCaseReply = upload_image.upload_image(
            store_image_request
        )
        return {
            "statusCode": 200,
            "image_key": store_image_reply.image_key,
        }
    except KeyError as e:
        logger.error(f"Missing required field in event: {e}")
        return {"statusCode": 400, "body": f"Missing required field: {e}"}
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {"statusCode": 500, "body": f"Internal server error: {e}"}


def __to_store_image_request(event: Dict[str, Any]) -> StoreImageUseCaseRequest:
    required_fields = ["image_name", "image_extension", "image_bytes"]
    for field in required_fields:
        if field not in event:
            raise KeyError(field)

    image_extension = ImageExtension.from_extension(event["image_extension"])
    if image_extension is None:
        raise ValueError(f"Invalid image extension: {event['image_extension']}")

    return StoreImageUseCaseRequest(
        image_name=event["image_name"],
        image_extension=image_extension,
        image_bytes=base64.b64decode(event["image_bytes"]),
    )
