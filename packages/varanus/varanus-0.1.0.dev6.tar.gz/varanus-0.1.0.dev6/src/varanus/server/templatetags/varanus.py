from django import template

from ..models import Log

register = template.Library()


@register.filter
def truncatepath(path: str, num: int = 50):
    if len(path) > num:
        parts = path.split("/")
        while len("/".join(parts)) > num:
            parts.pop(0)
        return "…" + "/".join(parts)
    return path


@register.filter
def levelname(level: int):
    return Log.level_name(level)
