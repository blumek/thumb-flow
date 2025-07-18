import unittest

from dev_blumek_upload_handler.domain.types.image_extension import ImageExtension
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway_model import (
    StoreImageGatewayRequest,
)
from dev_blumek_upload_handler.infrastructure.policy.extension_image_policy import (
    ExtensionImagePolicy,
)


class TestImagePolicyExtension(unittest.TestCase):
    def test_should_be_valid_when_image_extension_is_allowed(self):
        given_policy: ExtensionImagePolicy = self.given_extension_image_policy()
        given_request: StoreImageGatewayRequest = (
            self.given_store_image_gateway_request_with_extension(ImageExtension.PNG)
        )

        actual_result: bool = given_policy.is_valid(given_request)

        self.assertTrue(actual_result)

    @staticmethod
    def given_extension_image_policy() -> ExtensionImagePolicy:
        allowed_extensions = {ImageExtension.PNG, ImageExtension.JPG}
        return ExtensionImagePolicy(allowed_extensions=allowed_extensions)

    @staticmethod
    def given_store_image_gateway_request_with_extension(
        given_extension: ImageExtension,
    ) -> StoreImageGatewayRequest:
        return StoreImageGatewayRequest(
            image_name="given_name",
            image_extension=given_extension,
            image_bytes=b"given_image_bytes",
        )

    def test_should_be_invalid_when_image_extension_is_not_allowed(self):
        given_policy: ExtensionImagePolicy = self.given_extension_image_policy()
        given_request: StoreImageGatewayRequest = (
            self.given_store_image_gateway_request_with_extension(ImageExtension.GIF)
        )

        actual_result: bool = given_policy.is_valid(given_request)

        self.assertFalse(actual_result)


if __name__ == "__main__":
    unittest.main()
