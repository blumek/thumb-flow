import re
import unittest

from dev_blumek_upload_handler.infrastructure.factory.unique_image_key_factory import UniqueImageKeyFactory

expected_key_pattern = (
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}-.*$"
)


class TestUniqueImageKeyFactory(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uniqueImageKeyFactory: UniqueImageKeyFactory = UniqueImageKeyFactory()

    def test_should_create_key_with_uuid_prefix_and_image_name(self):
        given_image_name: str = self.given_image_name()

        actual_key: str = self.uniqueImageKeyFactory.create_key(given_image_name)

        self.then_image_key_should_follow_expected_pattern(actual_key)

    @staticmethod
    def given_image_name():
        return "given_name.png"

    def then_image_key_should_follow_expected_pattern(self, actual_key):
        self.assertTrue(
            re.match(expected_key_pattern, actual_key),
            f"Key does not match expected key pattern: {actual_key}",
        )
        self.assertTrue(actual_key.endswith(f"-{self.given_image_name()}"))

    def test_should_create_different_keys_for_same_image_name(self):
        given_image_name: str = self.given_image_name()

        actual_first_key: str = self.uniqueImageKeyFactory.create_key(given_image_name)
        actual_second_key: str = self.uniqueImageKeyFactory.create_key(given_image_name)

        self.then_two_valid_but_different_keys_were_created(
            actual_first_key, actual_second_key
        )

    def then_two_valid_but_different_keys_were_created(self, first_key, second_key):
        self.assertNotEqual(first_key, second_key)
        self.assertTrue(first_key.endswith(f"-{self.given_image_name()}"))
        self.assertTrue(second_key.endswith(f"-{self.given_image_name()}"))


if __name__ == "__main__":
    unittest.main()
