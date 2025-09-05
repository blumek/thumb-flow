import base64
import json
import logging
from typing import Dict, Any, cast, Tuple, Type

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

error_mappings: Dict[Type[Exception], Tuple[int, str]] = {
    KeyError: (400, "Missing required field"),
    ValueError: (400, "Invalid data format"),
    Exception: (500, "Internal server error"),
}

required_fields: list[str] = [
    "image_name",
    "image_extension",
    "image_bytes",
    "prompt",
]


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    try:
        body: dict[str, Any] = __extract_body_from_api_gateway_event(event)

        initialize_thumbnail_generation_request: (
            InitializeThumbnailGenerationUseCaseRequest
        ) = __to_initialize_thumbnail_generation_request(body)
        initialize_thumbnail_generation_reply: (
            InitializeThumbnailGenerationUseCaseReply
        ) = use_case.upload_image(initialize_thumbnail_generation_request)

        return __to_reply(initialize_thumbnail_generation_reply)
    except Exception as exception:
        error_type: Type[Exception] = type(exception)
        status_code: int
        message_prefix: str
        status_code, message_prefix = error_mappings.get(
            error_type, error_mappings[Exception]
        )

        logger.error(f"{message_prefix}: {exception}")
        return __to_error_reply(status_code, f"{message_prefix}: {str(exception)}")


def __extract_body_from_api_gateway_event(event: Dict[str, Any]) -> Dict[str, Any]:
    try:
        body: Any = event["body"]
    except KeyError:
        logger.error("No body found in event")
        raise KeyError("body")

    if isinstance(body, str):
        return __as_dict(body)

    if isinstance(body, dict):
        return body

    error_msg: str = f"Unexpected body type: {type(body).__name__}"
    logger.error(error_msg)
    raise ValueError(error_msg)


def __as_dict(body: Any) -> Dict[str, Any]:
    try:
        parsed: Any = json.loads(body)
        if not isinstance(parsed, dict):
            logger.error("Parsed body is not a JSON object")
            raise ValueError("Request body must be a JSON object")
        return cast(Dict[str, Any], parsed)
    except json.JSONDecodeError as exception:
        logger.error(f"Failed to parse body as JSON: {exception}")
        raise ValueError(f"Invalid JSON in request body: {exception}")


def __to_initialize_thumbnail_generation_request(
    body: Dict[str, Any],
) -> InitializeThumbnailGenerationUseCaseRequest:
    for field in required_fields:
        if field not in body:
            raise KeyError(field)

    return InitializeThumbnailGenerationUseCaseRequest(
        image_name=body["image_name"],
        image_extension=ImageExtension.from_extension(body["image_extension"]),
        image_bytes=base64.b64decode(body["image_bytes"]),
        prompt=body["prompt"],
    )


def __to_reply(
    initialize_thumbnail_generation_reply: InitializeThumbnailGenerationUseCaseReply,
) -> Dict[str, Any]:
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(
            {
                "workflow_id": initialize_thumbnail_generation_reply.workflow_id,
                "image_key": initialize_thumbnail_generation_reply.image_key,
            }
        ),
    }


def __to_error_reply(status_code: int, message: str) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({"error": message}),
    }
