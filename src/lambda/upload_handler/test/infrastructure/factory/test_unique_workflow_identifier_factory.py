import re
import unittest

from dev_blumek_upload_handler.infrastructure.factory.unique_workflow_identifier_factory import (
    UniqueWorkflowIdentifierFactory,
)

expected_uuid_pattern: str = (
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)


class TestUniqueWorkflowIdentifierFactory(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.uniqueWorkflowIdentifierFactory: UniqueWorkflowIdentifierFactory = (
            UniqueWorkflowIdentifierFactory()
        )

    def test_should_create_identifier_with_uuid_format(self) -> None:
        actual_identifier: str = (
            self.uniqueWorkflowIdentifierFactory.create_identifier()
        )

        self.then_identifier_should_follow_expected_pattern(actual_identifier)

    def then_identifier_should_follow_expected_pattern(
        self, actual_identifier: str
    ) -> None:
        self.assertTrue(
            re.match(expected_uuid_pattern, actual_identifier),
            f"Identifier does not match expected UUID pattern: {actual_identifier}",
        )

    def test_should_create_different_identifiers_for_multiple_calls(self) -> None:
        actual_first_identifier: str = (
            self.uniqueWorkflowIdentifierFactory.create_identifier()
        )
        actual_second_identifier: str = (
            self.uniqueWorkflowIdentifierFactory.create_identifier()
        )

        self.then_two_valid_but_different_identifiers_were_created(
            actual_first_identifier, actual_second_identifier
        )

    def then_two_valid_but_different_identifiers_were_created(
        self, first_identifier: str, second_identifier: str
    ) -> None:
        self.assertNotEqual(first_identifier, second_identifier)
        self.then_identifier_should_follow_expected_pattern(first_identifier)
        self.then_identifier_should_follow_expected_pattern(second_identifier)


if __name__ == "__main__":
    unittest.main()
