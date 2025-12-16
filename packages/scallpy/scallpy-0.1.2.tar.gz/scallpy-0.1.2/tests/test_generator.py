import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from scallfold.project.generator import create_project


def test_create_clean_project():
    """Test creating a clean project."""
    meta = {
        "project_name": "test_clean",
        "style": "clean",
        "use_db": False,
        "use_orm": False,
        "include_tests": True,
        "description": "Test project",
        "version": "0.1.0",
    }

    with TemporaryDirectory() as temp_dir:
        root_path = Path(temp_dir)
        create_project(meta, root_path)

        project_dir = root_path / "test_clean"
        assert project_dir.exists()
        assert (project_dir / "src" / "test_clean" / "main.py").exists()
        assert (project_dir / "pyproject.toml").exists()
        assert (project_dir / "tests" / "test_basic.py").exists()


def test_create_structured_project():
    """Test creating a structured project."""
    meta = {
        "project_name": "test_structured",
        "style": "structured",
        "use_db": False,
        "use_orm": False,
        "include_tests": True,
        "description": "Test project",
        "version": "0.1.0",
    }

    with TemporaryDirectory() as temp_dir:
        root_path = Path(temp_dir)
        create_project(meta, root_path)

        project_dir = root_path / "test_structured"
        assert project_dir.exists()
        assert (project_dir / "src" / "test_structured" / "main.py").exists()
        assert (project_dir / "src" / "test_structured" / "api" / "routes.py").exists()
        assert (project_dir / "pyproject.toml").exists()
        assert (project_dir / "tests" / "test_basic.py").exists()


def test_structured_project_with_db():
    """Test creating a structured project with database."""
    meta = {
        "project_name": "test_db",
        "style": "structured",
        "use_db": True,
        "use_orm": False,
        "include_tests": True,
        "description": "Test project",
        "version": "0.1.0",
    }

    with TemporaryDirectory() as temp_dir:
        root_path = Path(temp_dir)
        create_project(meta, root_path)

        project_dir = root_path / "test_db"
        assert (project_dir / "src" / "test_db" / "core" / "database.py").exists()


def test_structured_project_with_orm():
    """Test creating a structured project with ORM."""
    meta = {
        "project_name": "test_orm",
        "style": "structured",
        "use_db": True,
        "use_orm": True,
        "include_tests": True,
        "description": "Test project",
        "version": "0.1.0",
    }

    with TemporaryDirectory() as temp_dir:
        root_path = Path(temp_dir)
        create_project(meta, root_path)

        project_dir = root_path / "test_orm"
        assert (project_dir / "src" / "test_orm" / "models" / "base.py").exists()
        assert (project_dir / "src" / "test_orm" / "models" / "user.py").exists()


def test_project_without_tests():
    """Test creating a project without tests."""
    meta = {
        "project_name": "test_no_tests",
        "style": "clean",
        "use_db": False,
        "use_orm": False,
        "include_tests": False,
        "description": "Test project",
        "version": "0.1.0",
    }

    with TemporaryDirectory() as temp_dir:
        root_path = Path(temp_dir)
        create_project(meta, root_path)

        project_dir = root_path / "test_no_tests"
        assert not (project_dir / "tests").exists()


def test_unknown_style():
    """Test error on unknown project style."""
    meta = {
        "project_name": "test_unknown",
        "style": "unknown",
        "use_db": False,
        "use_orm": False,
        "include_tests": True,
        "description": "Test project",
        "version": "0.1.0",
    }

    with TemporaryDirectory() as temp_dir:
        root_path = Path(temp_dir)
        with pytest.raises(ValueError, match="Unknown project style"):
            create_project(meta, root_path)