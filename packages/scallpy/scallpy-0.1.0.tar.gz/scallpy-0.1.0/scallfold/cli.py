import typer
from pathlib import Path
from typing import Optional
from InquirerPy import inquirer
from enum import Enum
import re # Import the re module for regular expressions

from scallfold.compatibility import run as check_env, check_write_permissions
from scallfold.project.generator import create_project
from scallfold.utils.prompts import collect_project_meta

app = typer.Typer()

class ProjectStyle(str, Enum):
    clean = "clean"
    structured = "structured"

def _validate_project_name(value: str) -> str:
    """Validate project name to be a valid Python identifier."""
    if value is None:
        return None
    if not re.fullmatch(r"^[a-zA-Z_][a-zA-Z0-9_]*$", value):
        # Sanitize the name by replacing invalid characters with underscores
        # and ensuring it starts with a letter or underscore
        sanitized_name = re.sub(r"[^a-zA-Z0-9_]", "_", value)
        if not re.match(r"^[a-zA-Z_]", sanitized_name):
            sanitized_name = "_" + sanitized_name

        typer.secho(
            f"Warning: Project name '{value}' is not a valid Python identifier. "
            f"It has been sanitized to '{sanitized_name}'.",
            fg=typer.colors.YELLOW,
        )
        return sanitized_name
    return value

@app.callback()
def main():
    check_env()


@app.command()
def create(
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Name of the project.", callback=_validate_project_name
    ),
    style: Optional[ProjectStyle] = typer.Option(
        None, "--type", "-t", help="Type of project structure ('clean' or 'structured')."
    ),
    use_db: Optional[bool] = typer.Option(
        None, "--use-db", help="Include database support."
    ),
    use_orm: Optional[bool] = typer.Option(
        None, "--use-orm", help="Include ORM support."
    ),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to create the project in."
    ),
):
    """
    Creates a new FastAPI project.
    """
    if name and style:
        # If arguments are provided, bypass interactive prompts
        meta = {
            "project_name": name,
            "style": style.value, # Access the value of the Enum
            "use_db": use_db if use_db is not None else False,
            "use_orm": use_orm if use_orm is not None else False,
            "include_tests": True,
            "description": "",
            "version": "0.1.0",
        }
    else:
        # Otherwise, run the interactive prompts
        meta = collect_project_meta()

    # Validate flag consistency with improved error messages
    if meta.get("use_orm") and not meta.get("use_db"):
        typer.secho(
            "Error: Enable --use-db before using --use-orm. Example: --use-db --use-orm",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    if meta["style"] == "clean" and (meta.get("use_db") or meta.get("use_orm")):
        typer.secho(
            "Warning: --use-db and --use-orm are ignored with '--type clean'. Use '--type structured' for database features.",
            fg=typer.colors.YELLOW,
        )

    # Determine the target path and check for write permissions
    target_path = path if path else Path(".")
    check_write_permissions(str(target_path))

    try:
        # Pass the path to the generator. If path is None, it defaults to the project name.
        create_project(meta, root_path=path)
    except FileExistsError as e:
        typer.secho("Error: Project directory already exists. Choose a different name or path.", fg=typer.colors.RED)
        raise typer.Exit(1)
    except PermissionError:
        typer.secho("Error: Permission denied. Check write permissions or select another directory.", fg=typer.colors.RED)
        raise typer.Exit(1)
    except Exception as e:
        typer.secho(f"Unexpected error: {e}. Check your inputs or try again.", fg=typer.colors.RED)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
