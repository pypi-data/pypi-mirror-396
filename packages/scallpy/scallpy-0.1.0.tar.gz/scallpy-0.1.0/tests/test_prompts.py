import pytest
from scallfold.utils.prompts import PROJECT_NAME_PATTERN
import re


def test_project_name_pattern():
    """Test project name validation pattern."""
    assert re.match(PROJECT_NAME_PATTERN, "valid_name")
    assert re.match(PROJECT_NAME_PATTERN, "valid-name")
    assert re.match(PROJECT_NAME_PATTERN, "ValidName")
    assert re.match(PROJECT_NAME_PATTERN, "_valid")
    assert not re.match(PROJECT_NAME_PATTERN, "123invalid")
    assert not re.match(PROJECT_NAME_PATTERN, "invalid name")
    assert not re.match(PROJECT_NAME_PATTERN, "invalid@name")


# Note: collect_project_meta() requires interactive input, so it's hard to unit test.
# Integration tests or mocking would be needed for full coverage.