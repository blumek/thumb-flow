import unittest

from dev_blumek_upload_handler.domain.types.image_extension import ImageExtension
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway_model import StoreImageGatewayRequest
from dev_blumek_upload_handler.infrastructure.policy.composite_image_policy import CompositeImagePolicy
from dev_blumek_upload_handler.infrastructure.policy.image_policy import ImagePolicy


class TestImagePolicyComposite(unittest.TestCase):

    def test_should_be_valid_when_no_policies(self):
        given_composite_policy: CompositeImagePolicy = CompositeImagePolicy()
        given_request = self.given_store_image_gateway_request()

        actual_result: bool = given_composite_policy.is_valid(given_request)

        self.assertTrue(actual_result)

    @staticmethod
    def given_store_image_gateway_request() -> StoreImageGatewayRequest:
        return StoreImageGatewayRequest(
            image_name="given_name",
            image_extension=ImageExtension.PNG,
            image_bytes=b"given_image_bytes",
        )

    def test_should_be_valid_when_all_policies_pass(self):
        given_composite_policy: CompositeImagePolicy = (
            self.given_composite_policy_with_policies(
                self.given_passing_policy(), self.given_passing_policy()
            )
        )
        given_request = self.given_store_image_gateway_request()

        actual_result: bool = given_composite_policy.is_valid(given_request)

        self.assertTrue(actual_result)

    @staticmethod
    def given_composite_policy_with_policies(
        *policies: ImagePolicy,
    ) -> CompositeImagePolicy:
        return CompositeImagePolicy(*policies)

    @staticmethod
    def given_passing_policy() -> ImagePolicy:
        class PassingPolicy(ImagePolicy):
            def is_valid(self, image_store_request: StoreImageGatewayRequest) -> bool:
                return True

        return PassingPolicy()

    def test_should_be_invalid_when_any_policy_fails(self):
        given_composite_policy: CompositeImagePolicy = (
            self.given_composite_policy_with_policies(
                self.given_failing_policy(), self.given_passing_policy()
            )
        )
        given_request = self.given_store_image_gateway_request()

        actual_result: bool = given_composite_policy.is_valid(given_request)

        self.assertFalse(actual_result)

    @staticmethod
    def given_failing_policy() -> ImagePolicy:
        class FailingPolicy(ImagePolicy):
            def is_valid(self, image_store_request: StoreImageGatewayRequest) -> bool:
                return False

        return FailingPolicy()


if __name__ == "__main__":
    unittest.main()
