import sys
import shutil
import os
import typer

MIN_VERSION = (3, 10)
MAX_VERSION = (3, 13)

def check_python_version():
    major, minor = sys.version_info[:2]

    if not (MIN_VERSION <= (major, minor) <= MAX_VERSION):
        typer.secho(
            f"Python {major}.{minor} is not supported. "
            f"Required: {MIN_VERSION[0]}.{MIN_VERSION[1]}–{MAX_VERSION[0]}.{MAX_VERSION[1]}",
            fg="red"
        )
        raise typer.Exit(1)


def check_required_tools():
    required = ["python3", "pip"]

    for tool in required:
        if shutil.which(tool) is None:
            typer.secho(f"Missing required tool: {tool}", fg="red")
            raise typer.Exit(1)


def check_write_permissions(path="."):
    if not os.access(path, os.W_OK):
        typer.secho(f"No write permissions in: {os.path.abspath(path)}", fg="red")
        raise typer.Exit(1)


def run():
    check_python_version()
    check_required_tools()

