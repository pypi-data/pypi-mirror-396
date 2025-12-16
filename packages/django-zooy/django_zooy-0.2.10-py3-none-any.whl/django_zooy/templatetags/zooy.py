import uuid

from django import template

register = template.Library()


@register.simple_tag
def rand_id(prefix="id"):
    """Generate a random ID for form elements"""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"
