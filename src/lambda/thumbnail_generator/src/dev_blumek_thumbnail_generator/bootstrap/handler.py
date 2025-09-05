import json
import logging
from typing import Dict, Any, List, Tuple, Type

from aws_lambda_typing.context import Context as LambdaContext

from dev_blumek_thumbnail_generator.application.use_case.generate_thumbail_use_case_model import (
    GenerateThumbnailUseCaseRequest,
)
from dev_blumek_thumbnail_generator.bootstrap.application_bootstrap import (
    generate_thumbnail_use_case,
)

generate_thumbnail = generate_thumbnail_use_case()
logger = logging.getLogger(__name__)

error_mappings: Dict[Type[Exception], Tuple[int, str]] = {
    KeyError: (400, "Missing required field"),
    ValueError: (400, "Invalid data format"),
    Exception: (500, "Internal server error"),
}

required_fields: list[str] = [
    "workflow_id",
    "uploaded_image_key",
    "prompt",
]


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    if not event.get("Records"):
        logger.error("Event does not contain Records")
        return {"statusCode": 400, "body": "Invalid SQS event format"}

    responses: List[Dict[str, Any]] = []
    for record in event.get("Records", []):
        responses.append(__generate_thumbnail(record))

    status_code: int = 200 if all(r.get("success", False) for r in responses) else 207

    return {
        "statusCode": status_code,
        "body": json.dumps({"responses": responses}),
    }


def __generate_thumbnail(record: Dict[str, Any]) -> Dict[str, Any]:
    try:
        thumbnail_request: GenerateThumbnailUseCaseRequest = (
            _to_generate_thumbnail_request(record)
        )
        thumbnail_reply = generate_thumbnail.generate_thumbnail(thumbnail_request)
        return {
            "statusCode": 200,
            "image_key": thumbnail_reply.thumbnail_key,
            "success": True,
        }
    except Exception as exception:
        error_type: Type[Exception] = type(exception)
        status_code: int
        message_prefix: str
        status_code, message_prefix = error_mappings.get(
            error_type, error_mappings[Exception]
        )

        return {
            "statusCode": status_code,
            "error": f"{message_prefix}: {str(exception)}",
            "success": False,
        }


def _to_generate_thumbnail_request(
    record: Dict[str, Any],
) -> GenerateThumbnailUseCaseRequest:
    try:
        message_body: Dict[str, Any] = (
            json.loads(record["body"]) if "body" in record else record
        )

        for field in required_fields:
            if field not in message_body:
                raise KeyError(field)

        return GenerateThumbnailUseCaseRequest(
            workflow_id=message_body["workflow_id"],
            image_key=message_body["uploaded_image_key"],
            prompt=message_body["prompt"],
        )
    except json.JSONDecodeError:
        logger.error("Invalid JSON in SQS message body")
        raise ValueError("Invalid JSON in SQS message body")
