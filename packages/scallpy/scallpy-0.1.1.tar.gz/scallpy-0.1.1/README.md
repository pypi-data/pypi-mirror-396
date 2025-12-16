# scallpy

A command-line tool to scaffold FastAPI projects, inspired by `vitejs`.

## Overview

`scallpy` helps you quickly set up new FastAPI projects with sensible defaults, providing both a "clean" and a "structured" project template.

## Installation

### For Users

**Requirements:** Python 3.10 or higher.

To install `scallpy` and use it to create new projects, it's recommended to use `pipx`. This ensures `scallpy` and its dependencies are installed in an isolated environment without affecting your global Python packages.

```bash
pipx install scallpy
```

After installation, you can use the `scallpy` command globally.

### For Developers (Contributing to scallpy)

If you want to contribute to `scallpy` or modify its source code:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/jara505/fastapi-scallfolding.git
    cd fastapi-scallfolding
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install in editable mode with dev dependencies:**
    ```bash
    pip install -e ".[dev]"
    ```
4.  **Run tests:**
    ```bash
    pytest
    ```

**Note:** For stability, use Poetry 1.x (e.g., `pip install poetry==1.8.3`) when working with generated projects. Poetry 2.x may have compatibility issues.

## Usage

`scallpy` provides a `create` command to generate new FastAPI projects.

### Interactive Mode

To create a project interactively, simply run:

```bash
scallpy create
```
The CLI will guide you through selecting a project name, type, and other options.

### Non-Interactive Mode (with parameters)

You can also provide parameters directly to bypass interactive prompts, which is useful for scripting or quick setups.

```bash
scallpy create --name <project-name> --type <project-type> [--use-db] [--use-orm] [--path <output-path>]
```

**Parameters:**

*   `--name` or `-n`: The name of your new FastAPI project. This will also be the name of the directory created for your project.
*   `--type` or `-t`: The type of project structure to generate.
    *   `clean`: A minimal FastAPI project with a single `main.py` file.
    *   `structured`: A more organized FastAPI project with separate modules for API routes, core configuration, and models.
*   `--use-db` (Optional): Include database support in the project. Use as a flag (e.g., `--use-db`).
*   `--use-orm` (Optional): Include ORM (Object-Relational Mapper) support in the project. Use as a flag (e.g., `--use-orm`).
*   `--path` or `-p` (Optional): The directory where the new project folder will be created. If not specified, the project will be created in the current working directory. If `.` is provided, the project folder will be created inside the current directory.

**Example:**

```bash
scallpy create --name my-awesome-api --type structured --path ./projects
```

## Running Your Generated Project

After `scallpy` creates your project, it will provide specific instructions. Generally, the steps are:

1.  **Navigate into your new project directory:**
    ```bash
    cd <your-project-name>
    ```
2.  **Install dependencies using Poetry:**
    ```bash
    poetry install
    ```
3.  **Run the FastAPI development server:**
    *   **For `clean` projects:**
        ```bash
        poetry run uvicorn <your-project-name>.main:app --reload
        ```
    *   **For `structured` projects:**
        ```bash
        poetry run uvicorn <your-project-name>.main:app --reload
        ```
    (Replace `<your-project-name>` with the actual name you gave your project).

Your FastAPI application will typically be available at `http://127.0.0.1:8000`.

## Contributing

We welcome contributions! Please feel free to open issues or submit pull requests.

## Testing

To run the test suite:
```bash
pytest
```

Ensure all tests pass before submitting pull requests.

## License

This project is licensed under the MIT License.
