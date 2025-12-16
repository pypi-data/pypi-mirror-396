from typing import Dict, Any
from InquirerPy import inquirer
import re


PROJECT_NAME_PATTERN = r"^[a-zA-Z_][a-zA-Z0-9_-]*$"


def collect_project_meta() -> Dict[str, Any]:
    # Collect project metadata interactively with improved prompts
    name = inquirer.text(
        message="What is your project name?",
        validate=lambda s: re.match(PROJECT_NAME_PATTERN, s) is not None,
        invalid_message="Invalid project name. Use letters, numbers, underscore, and hyphen.",
    ).execute()

    style = inquirer.select(message="What project type do you want? (clean: simple with one file; structured: modular with folders)",
                            choices=["clean", "structured"]).execute()

    include_tests = inquirer.confirm(
        message="Include basic tests?", default=True
    ).execute()

    description = inquirer.text(
        message="Project description (optional):", default=""
    ).execute()

    version = inquirer.text(message="Project version:", default="0.1.0").execute()

    use_db = False
    use_orm = False
    if style != "clean":
        # Additional options for structured projects
        use_db = inquirer.confirm(
            message="Include database support?", default=False
        ).execute()
        use_orm = inquirer.confirm(
            message="Include ORM support?", default=False
        ).execute()

    return {
        "project_name": name,
        "style": style,
        "use_db": use_db,
        "use_orm": use_orm,
        "include_tests": include_tests,
        "description": description,
        "version": version,
    }
