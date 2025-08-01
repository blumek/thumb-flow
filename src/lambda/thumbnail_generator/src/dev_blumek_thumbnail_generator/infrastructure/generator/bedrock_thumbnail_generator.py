import base64
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from botocore.response import StreamingBody
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient
from mypy_boto3_bedrock_runtime.type_defs import InvokeModelResponseTypeDef

from dev_blumek_thumbnail_generator.infrastructure.generator.seed_generator import (
    SeedGenerator,
)
from dev_blumek_thumbnail_generator.infrastructure.generator.thumbnail_generator import (
    ThumbnailGenerator,
)
from dev_blumek_thumbnail_generator.infrastructure.generator.thumbnail_generator_model import (
    GenerateThumbnailRequest,
    GenerateThumbnailReply,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BedrockConfiguration:
    model_id: str = "stability.stable-diffusion-xl-v1"
    image_strength: float = 0.8
    cfg_scale: int = 7
    steps: int = 40

    def __post_init__(self) -> None:
        if not 0.0 <= self.image_strength <= 1.0:
            raise ValueError("image_strength must be between 0.0 and 1.0")
        if not 1 <= self.cfg_scale <= 20:
            raise ValueError("cfg_scale must be between 1 and 20")
        if not 10 <= self.steps <= 150:
            raise ValueError("steps must be between 10 and 150")


class BedrockThumbnailGenerator(ThumbnailGenerator):
    def __init__(
        self,
        bedrock_client: BedrockRuntimeClient,
        configuration: BedrockConfiguration,
        seed_generator: SeedGenerator,
    ) -> None:
        self._bedrock_client = bedrock_client
        self._config = configuration
        self._seed_generator = seed_generator

    def generate_thumbnail(
        self, request: GenerateThumbnailRequest
    ) -> GenerateThumbnailReply:
        try:
            model_request: Dict[str, Any] = self.__build_model_request(request)
            response: InvokeModelResponseTypeDef = self.__invoke_bedrock_model(
                model_request
            )
            thumbnail_bytes: bytes = self.__extract_thumbnail_bytes(response)
            return GenerateThumbnailReply(thumbnail_bytes=thumbnail_bytes)
        except BedrockThumbnailGenerationError:
            raise
        except Exception as exception:
            logger.error(
                "Error occurred during thumbnail generation", exc_info=exception
            )
            raise BedrockThumbnailGenerationError(
                f"Unexpected error during thumbnail generation: {exception}"
            ) from exception

    def __build_model_request(
        self, request: GenerateThumbnailRequest
    ) -> Dict[str, Any]:
        seed: int = (
            request.seed
            if request.seed is not None
            else self._seed_generator.generate()
        )

        base64_image = base64.b64encode(request.input_image_bytes).decode("utf-8")

        return {
            "init_image": base64_image,
            "prompt": request.prompt,
            "image_strength": self._config.image_strength,
            "cfg_scale": self._config.cfg_scale,
            "steps": self._config.steps,
            "seed": seed,
        }

    def __invoke_bedrock_model(
        self, model_request: Dict[str, Any]
    ) -> InvokeModelResponseTypeDef:
        try:
            return self._bedrock_client.invoke_model(
                modelId=self._config.model_id,
                body=json.dumps(model_request),
                contentType="application/json",
                accept="application/json",
            )
        except Exception as e:
            raise BedrockThumbnailGenerationError(
                f"Failed to invoke Bedrock model {self._config.model_id}: {e}"
            ) from e

    def __extract_thumbnail_bytes(self, response: InvokeModelResponseTypeDef) -> bytes:
        body: Optional[StreamingBody] = response.get("body")
        if not body:
            raise BedrockThumbnailGenerationError(
                "Invalid Bedrock response: No response body received"
            )

        return self.__read(body)

    @staticmethod
    def __read(body: StreamingBody) -> bytes:
        try:
            return body.read()
        except Exception as e:
            raise BedrockThumbnailGenerationError(f"Failed to read body: {e}") from e


class BedrockThumbnailGenerationError(Exception):
    pass
