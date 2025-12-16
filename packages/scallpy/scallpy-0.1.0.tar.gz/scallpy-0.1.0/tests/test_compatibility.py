import pytest
from scallfold.compatibility import check_python_version, check_required_tools, check_write_permissions
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from click.exceptions import Exit


def test_check_python_version_supported():
    """Test Python version check with supported version."""
    # Assuming current Python is supported (3.10-3.12)
    try:
        check_python_version()
    except SystemExit:
        pytest.fail("Python version check failed for supported version")


def test_check_required_tools():
    """Test required tools check."""
    # Assuming python3 and pip are available
    try:
        check_required_tools()
    except SystemExit:
        pytest.fail("Required tools check failed")


def test_check_write_permissions_valid():
    """Test write permissions check for valid directory."""
    with TemporaryDirectory() as temp_dir:
        try:
            check_write_permissions(temp_dir)
        except SystemExit:
            pytest.fail("Write permissions check failed for valid directory")


def test_check_write_permissions_invalid():
    """Test write permissions check for invalid directory."""
    # Use a non-existent or read-only path
    invalid_path = "/root/invalid"  # Assuming no write access
    with pytest.raises(Exit):
        check_write_permissions(invalid_path)