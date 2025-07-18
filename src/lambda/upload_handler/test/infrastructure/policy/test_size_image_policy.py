import unittest

from dev_blumek_upload_handler.domain.types.image_extension import ImageExtension
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway_model import StoreImageGatewayRequest
from dev_blumek_upload_handler.infrastructure.policy.size_image_policy import SizeImagePolicy


class TestSizeImagePolicy(unittest.TestCase):
    def test_should_be_valid_when_image_size_is_smaller_than_max_size(self):
        given_policy: SizeImagePolicy = self.given_size_image_policy_with_max_size(1000)
        given_request: StoreImageGatewayRequest = (
            self.given_store_image_gateway_request_with_image_of_size(500)
        )

        actual_result: bool = given_policy.is_valid(given_request)

        self.assertTrue(actual_result)

    @staticmethod
    def given_size_image_policy_with_max_size(max_size: int) -> SizeImagePolicy:
        return SizeImagePolicy(max_bytes_size=max_size)

    @staticmethod
    def given_store_image_gateway_request_with_image_of_size(
        image_size: int,
    ) -> StoreImageGatewayRequest:
        return StoreImageGatewayRequest(
            image_name="given_name",
            image_extension=ImageExtension.PNG,
            image_bytes=b"x" * image_size,
        )

    def test_should_be_valid_when_image_size_is_equal_to_max_size(self):
        given_policy: SizeImagePolicy = self.given_size_image_policy_with_max_size(1000)
        given_request: StoreImageGatewayRequest = (
            self.given_store_image_gateway_request_with_image_of_size(1000)
        )

        actual_result: bool = given_policy.is_valid(given_request)

        self.assertTrue(actual_result)

    def test_should_be_valid_when_image_size_exceeds_max_size(self):
        given_policy: SizeImagePolicy = self.given_size_image_policy_with_max_size(500)
        given_request: StoreImageGatewayRequest = (
            self.given_store_image_gateway_request_with_image_of_size(1000)
        )

        actual_result: bool = given_policy.is_valid(given_request)

        self.assertFalse(actual_result)


if __name__ == "__main__":
    unittest.main()
