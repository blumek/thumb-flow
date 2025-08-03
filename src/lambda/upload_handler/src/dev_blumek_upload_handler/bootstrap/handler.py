import base64
import logging
from typing import Dict, Any

from aws_lambda_typing.context import Context as LambdaContext

from dev_blumek_upload_handler.bootstrap.application_bootstrap import (
    initialize_thumbnail_generation_use_case as init_use_case,
)
from dev_blumek_upload_handler.domain.types.image_extension import ImageExtension
from dev_blumek_upload_handler.application.use_case.initialize_thumbnail_generation_use_case_model import (
    InitializeThumbnailGenerationUseCaseRequest,
    InitializeThumbnailGenerationUseCaseReply,
)

use_case = init_use_case()
logger = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    try:
        initialize_thumbnail_generation_request: (
            InitializeThumbnailGenerationUseCaseRequest
        ) = __to_initialize_thumbnail_generation_request(event)
        initialize_thumbnail_generation_reply: (
            InitializeThumbnailGenerationUseCaseReply
        ) = use_case.upload_image(initialize_thumbnail_generation_request)
        return {
            "statusCode": 200,
            "image_key": initialize_thumbnail_generation_reply.image_key,
        }
    except KeyError as e:
        logger.error(f"Missing required field in event: {e}")
        return {"statusCode": 400, "body": f"Missing required field: {e}"}
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {"statusCode": 500, "body": f"Internal server error: {e}"}


def __to_initialize_thumbnail_generation_request(
    event: Dict[str, Any],
) -> InitializeThumbnailGenerationUseCaseRequest:
    required_fields: list[str] = [
        "image_name",
        "image_extension",
        "image_bytes",
        "prompt",
    ]
    for field in required_fields:
        if field not in event:
            raise KeyError(field)

    return InitializeThumbnailGenerationUseCaseRequest(
        image_name=event["image_name"],
        image_extension=ImageExtension.from_extension(event["image_extension"]),
        image_bytes=base64.b64decode(event["image_bytes"]),
        prompt=event["prompt"],
    )
