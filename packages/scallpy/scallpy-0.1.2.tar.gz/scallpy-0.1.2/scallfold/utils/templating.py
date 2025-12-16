from pathlib import Path
from typing import Dict, Any
from jinja2 import Template

BASE_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def get_template_path(style: str, name: str) -> Path:
    """
    Constructs the path to a template file.
    """
    path = BASE_TEMPLATE_DIR / style / name
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path


def render_template(path: Path, ctx: Dict[str, Any]) -> str:
    """
    Renders a Jinja2 template with the given context.
    """
    content = path.read_text()
    template = Template(content)
    return template.render(**ctx)
