from typing import Dict, Any

from jinja2 import Template


def render_template_string(template_str: str, state: Dict[str, Any]) -> str:
    template = Template(template_str)
    return template.render(state)