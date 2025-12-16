import pytest
from scallfold.project.structure import STRUCTURES


def test_structures_defined():
    """Test that project structures are defined."""
    assert "clean" in STRUCTURES
    assert "structured" in STRUCTURES

    clean = STRUCTURES["clean"]
    assert "dirs" in clean
    assert "templates" in clean
    assert "files" in clean

    structured = STRUCTURES["structured"]
    assert "dirs" in structured
    assert "templates" in structured
    assert "files" in structured
    assert "init_files" in structured


def test_clean_structure_has_required_keys():
    """Test clean structure has all required components."""
    clean = STRUCTURES["clean"]
    assert "src/{project_name}" in clean["dirs"]
    assert "tests" in clean["dirs"]
    assert "main.py.j2" in clean["templates"]
    assert "pyproject.toml.j2" in clean["templates"]
    assert ".gitignore" in clean["files"]


def test_structured_structure_has_required_keys():
    """Test structured structure has all required components."""
    structured = STRUCTURES["structured"]
    assert "src/{project_name}/api" in structured["dirs"]
    assert "src/{project_name}/core" in structured["dirs"]
    assert "src/{project_name}/models" in structured["dirs"]
    assert "tests" in structured["dirs"]
    assert "main.py.j2" in structured["templates"]
    assert "api/routes.py.j2" in structured["templates"]
    assert ".gitignore" in structured["files"]
    assert ".env" in structured["files"]