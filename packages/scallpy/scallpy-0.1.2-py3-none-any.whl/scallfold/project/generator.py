import typer
from pathlib import Path
from typing import Dict, Any, Optional

from scallfold.compatibility import check_python_version
from scallfold.project.structure import STRUCTURES
from scallfold.utils.filesystem import ensure_empty_directory
from scallfold.utils.templating import get_template_path, render_template


def create_project(meta: Dict[str, Any], root_path: Optional[Path] = None):
    """
    Generates a project structure based on metadata and a declarative structure map.
    """
    style = meta["style"]
    project_name = meta["project_name"]
    # If a path is provided, use it as the base. Otherwise, use the current directory.
    base_path = root_path.resolve() if root_path else Path(".")
    root = base_path / project_name

    ensure_empty_directory(root)

    base_structure = STRUCTURES.get(style)
    if not base_structure:
        raise ValueError(f"Unknown project style: {style}")

    # Make a copy to modify in-place
    structure = base_structure.copy()

    if style == "structured":
        if meta.get("use_db"):
            structure["templates"]["core/database.py.j2"] = "src/{project_name}/core/database.py"

        if meta.get("use_orm"):
            # 'models/base.py.j2' is used by the ORM example
            structure["templates"]["models/base.py.j2"] = "src/{project_name}/models/base.py"
            structure["templates"]["models/user.py.j2"] = "src/{project_name}/models/user.py"

    # If not including tests, remove test-related entries
    if not meta.get("include_tests"):
        if "tests" in structure.get("dirs", []):
            structure["dirs"] = [d for d in structure["dirs"] if d != "tests"]
        if "test_basic.py.j2" in structure.get("templates", {}):
            # Create a copy of the templates dict to modify it
            structure["templates"] = structure["templates"].copy()
            del structure["templates"]["test_basic.py.j2"]

    # Create directories
    for dir_path in structure.get("dirs", []):
        path = root / dir_path.format(**meta)
        path.mkdir(parents=True, exist_ok=True)

    # Render templates
    for template_name, output_path in structure.get("templates", {}).items():
        template_path = get_template_path(style, template_name)
        final_path = root / output_path.format(**meta)
        final_path.write_text(render_template(template_path, meta))

    # Copy static files
    for file_name, output_path in structure.get("files", {}).items():
        static_file_path = get_template_path(style, file_name)
        final_path = root / output_path.format(**meta)
        final_path.write_text(static_file_path.read_text())

    # Create empty __init__.py files
    for init_path in structure.get("init_files", []):
        path = root / init_path.format(**meta)
        path.touch()

    check_python_version()

    typer.secho(f"\nProject '{project_name}' created successfully!", fg=typer.colors.GREEN, bold=True)
    typer.secho("\nNext steps:", bold=True)

    # Use relative path for cd command if possible
    try:
        cd_path = Path(root).relative_to(Path.cwd())
    except ValueError:
        cd_path = root.resolve()

    typer.echo(f"  cd {cd_path}")
    typer.echo("  poetry install")

    if style == "structured":
        run_command = f"poetry run uvicorn {project_name}.main:app --reload"
        typer.secho(f"  {run_command}", bold=True)
    else: # clean - now main.py is also inside src/{project_name}
        run_command = f"poetry run uvicorn {project_name}.main:app --reload"
        typer.secho(f"  {run_command}", bold=True)
