from pathlib import Path


def ensure_empty_directory(path: Path):
    """
    Ensures the target directory does not exist, then creates it.
    """
    if path.exists():
        raise FileExistsError(f"Target directory already exists: {path}")
    path.mkdir(parents=True)
