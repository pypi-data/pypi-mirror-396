import pytest
from scallfold.utils.filesystem import ensure_empty_directory
from pathlib import Path
from tempfile import TemporaryDirectory


def test_ensure_empty_directory():
    """Test creating an empty directory."""
    with TemporaryDirectory() as temp_dir:
        new_dir = Path(temp_dir) / "new_dir"
        ensure_empty_directory(new_dir)
        assert new_dir.exists()
        assert new_dir.is_dir()


def test_ensure_empty_directory_exists():
    """Test error when directory already exists."""
    with TemporaryDirectory() as temp_dir:
        existing_dir = Path(temp_dir) / "existing"
        existing_dir.mkdir()
        with pytest.raises(FileExistsError):
            ensure_empty_directory(existing_dir)