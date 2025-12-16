"""
This module defines the project structures for different styles.
"""

# A mapping from template file names to their output paths.
# The output paths can contain placeholders that will be formatted
# with the project metadata (e.g., {project_name}).
STRUCTURES = {
    "clean": {
        "dirs": [
            "src/{project_name}",
            "tests",
        ],
        "templates": {
            "pyproject.toml.j2": "pyproject.toml",
            "README.md.j2": "README.md",
            "main.py.j2": "src/{project_name}/main.py",
            "package_init.py.j2": "src/{project_name}/__init__.py",
            "test_basic.py.j2": "tests/test_basic.py",
        },
        "files": {
            ".gitignore": ".gitignore",
        },
    },
    "structured": {
        "dirs": [
            "src/{project_name}/api",
            "src/{project_name}/core",
            "src/{project_name}/models",
            "tests",
        ],
        "templates": {
            "pyproject.toml.j2": "pyproject.toml",
            "README.md.j2": "README.md",
            "main.py.j2": "src/{project_name}/main.py",
            "api/routes.py.j2": "src/{project_name}/api/routes.py",
            "core/config.py.j2": "src/{project_name}/core/config.py",
            "requirements.txt.j2": "requirements.txt",
            "test_basic.py.j2": "tests/test_basic.py",
        },
        "files": {
            ".gitignore": ".gitignore",
            ".env": ".env",
        },
        "init_files": [
            "src/{project_name}/__init__.py",
            "src/{project_name}/api/__init__.py",
            "src/{project_name}/core/__init__.py",
            "src/{project_name}/models/__init__.py",
        ],
    },
}