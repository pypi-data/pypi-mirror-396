from __future__ import annotations

from django.core.exceptions import ValidationError
from django.template import Context, Engine


def render_string(template_str: str, context: dict) -> str:
    """
    Render a Django template string with strict missing-variable handling.
    """
    engine = Engine(debug=True, string_if_invalid="__INVALID__")
    template = engine.from_string(template_str or "")
    rendered = template.render(Context(context or {}, autoescape=False))
    if "__INVALID__" in rendered:
        raise ValidationError("Missing variables in notification template context.")
    return rendered
