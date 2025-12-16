# Agent Guidelines for fast-forge

This document outlines the conventions and commands for contributing to the `fast-forge` project.

## Build, Lint, and Test Commands

*   **Build**: `hatch build`
*   **Lint**: `ruff check .` (check), `ruff format .` (format)
*   **Test**:
    *   All tests: `pytest`
    *   Single file: `pytest <path/to/test_file.py>`
    *   Specific test: `pytest <path/to/test_file.py>::<test_function_name>`

## Code Style Guidelines

*   **General**: Adhere to PEP 8.
*   **Imports**: Group standard, third-party, and local imports. Sort alphabetically.
*   **Formatting**: Use `ruff format`.
*   **Types**: Use Python type hints.
*   **Naming**: Follow PEP 8 (`snake_case` for functions/variables, `CamelCase` for classes).
*   **Error Handling**: Use `try...except` for anticipated errors.
*   **Docstrings**: Provide clear docstrings for modules, classes, and functions.

## Git Commit Guidelines

1.  **Subject Line**: Provide a concise summary (50-70 characters) of the change.
2.  **Body (Optional)**: Include details on *why* the change was made, important decisions, and edge cases.
3.  **Voice**: Use active and imperative voice (e.g., "Fix bug," "Add feature").
4.  **Atomicity**: Each commit should be atomic, focusing on a single logical change (e.g., do not mix refactors, fixes, and features).
5.  **Language**: Always write commit messages in English.

## Pull Request Structure

1.  **Overview**: Provide a high-level summary of the changes, avoiding repetition of individual commit messages.
2.  **Content**: Include what was done, why it was done, and its impact on other modules.
3.  **Size**: Keep PRs small and focused; avoid "mega PRs."
4.  **Language**: Always write pull request descriptions in English.