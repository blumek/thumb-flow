import logging
from typing import Dict, Any

from aws_lambda_typing.context import Context as LambdaContext

from dev_blumek_thumbnail_generator.application.use_case.generate_thumbail_use_case_model import (
    GenerateThumbnailUseCaseRequest,
    GenerateThumbnailUseCaseReply,
)
from dev_blumek_thumbnail_generator.bootstrap.application_bootstrap import (
    generate_thumbnail_use_case,
)

generate_thumbnail = generate_thumbnail_use_case()
logger = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    try:
        generate_thumbnail_request: GenerateThumbnailUseCaseRequest = (
            __to_generate_thumbnail_request(event)
        )
        generate_thumbnail_reply: GenerateThumbnailUseCaseReply = (
            generate_thumbnail.generate_thumbnail(generate_thumbnail_request)
        )
        return {
            "statusCode": 200,
            "image_key": generate_thumbnail_reply.thumbnail_key,
        }
    except KeyError as e:
        logger.error(f"Missing required field in event: {e}")
        return {"statusCode": 400, "body": f"Missing required field: {e}"}
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {"statusCode": 500, "body": f"Internal server error: {e}"}


def __to_generate_thumbnail_request(
    event: Dict[str, Any],
) -> GenerateThumbnailUseCaseRequest:
    required_fields: list[str] = ["image_key", "prompt"]
    for field in required_fields:
        if field not in event:
            raise KeyError(field)

    return GenerateThumbnailUseCaseRequest(
        image_key=event["image_key"],
        prompt=event["prompt"],
    )
