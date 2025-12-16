from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django import template
from django.forms.utils import flatatt
from django.template.base import FilterExpression, Parser, Token
from django.template.context import Context
from django.utils.safestring import mark_safe

from ..brick import BlockBrick, Brick
from ..registry import get_registry

if TYPE_CHECKING:
    from django.template.base import NodeList

register = template.Library()


@register.filter
def attrs(value: dict[str, Any]) -> str:
    """
    Convert a dict to HTML attributes string.

    Underscores in keys are converted to hyphens (e.g., data_id -> data-id).
    Boolean True renders as just the attribute name (e.g., disabled=True -> disabled).
    Boolean False or None values are skipped.

    Usage:
        <div{{ extra|attrs }}>
        <button class="btn"{{ extra|attrs }}>
    """
    if not value:
        return ""

    # Convert underscores to hyphens and filter out False/None values
    converted = {}
    for key, val in value.items():
        if val is False or val is None:
            continue
        html_key = key.replace("_", "-")
        if val is True:
            converted[html_key] = html_key  # e.g., disabled="disabled"
        else:
            converted[html_key] = val

    return mark_safe(flatatt(converted))


def parse_tag_kwargs(parser: Parser, bits: list[str]) -> dict[str, Any]:
    """
    Parse keyword arguments from template tag bits.

    Handles:
        - kwarg="string value"
        - kwarg=variable
        - kwarg=variable|filter
        - kwarg=42 (integers)
        - kwarg=3.14 (floats)
        - kwarg=True/False (booleans)
    """
    kwargs: dict[str, Any] = {}

    for bit in bits:
        if "=" not in bit:
            raise template.TemplateSyntaxError(
                f"Invalid argument '{bit}'. Arguments must be in kwarg=value format."
            )

        name, value = bit.split("=", 1)

        # Handle booleans
        if value == "True":
            kwargs[name] = True
        elif value == "False":
            kwargs[name] = False
        # Handle None
        elif value == "None":
            kwargs[name] = None
        # Handle integers
        elif value.lstrip("-").isdigit():
            kwargs[name] = int(value)
        # Handle floats
        elif _is_float(value):
            kwargs[name] = float(value)
        # Handle as filter expression (supports variables, filters, and quoted strings)
        else:
            kwargs[name] = parser.compile_filter(value)

    return kwargs


def _is_float(value: str) -> bool:
    """Check if a string represents a float."""
    try:
        float(value)
        return "." in value or "e" in value.lower()
    except ValueError:
        return False


def resolve_kwargs(kwargs: dict[str, Any], context: Context) -> dict[str, Any]:
    """Resolve any filter expressions in kwargs."""
    resolved = {}
    for key, value in kwargs.items():
        if isinstance(value, FilterExpression):
            resolved[key] = value.resolve(context)
        else:
            resolved[key] = value
    return resolved


class BrickNode(template.Node):
    """Template node for simple (self-closing) bricks."""

    def __init__(
        self, brick_class: type[Brick], kwargs: dict[str, Any]
    ) -> None:
        self.brick_class = brick_class
        self.kwargs = kwargs

    def render(self, context: Context) -> str:
        resolved_kwargs = resolve_kwargs(self.kwargs, context)
        brick = self.brick_class(**resolved_kwargs)
        return mark_safe(brick.render(context=context.flatten()))


class BlockBrickNode(template.Node):
    """Template node for block bricks that wrap children."""

    def __init__(
        self,
        brick_class: type[BlockBrick],
        kwargs: dict[str, Any],
        nodelist: NodeList,
    ) -> None:
        self.brick_class = brick_class
        self.kwargs = kwargs
        self.nodelist = nodelist

    def render(self, context: Context) -> str:
        resolved_kwargs = resolve_kwargs(self.kwargs, context)
        children = self.nodelist.render(context)
        brick = self.brick_class(**resolved_kwargs)
        return mark_safe(brick.render(children=children, context=context.flatten()))


def create_simple_tag(brick_class: type[Brick]):
    """Create a simple tag function for a brick."""

    def tag_func(parser: Parser, token: Token) -> BrickNode:
        bits = token.split_contents()[1:]  # Skip the tag name
        kwargs = parse_tag_kwargs(parser, bits)
        return BrickNode(brick_class, kwargs)

    return tag_func


def create_block_tag(brick_class: type[BlockBrick]):
    """Create a block tag function for a brick."""
    tag_name = brick_class.get_brick_name()
    end_tag = f"end{tag_name}"

    def tag_func(parser: Parser, token: Token) -> BlockBrickNode:
        bits = token.split_contents()[1:]  # Skip the tag name
        kwargs = parse_tag_kwargs(parser, bits)
        nodelist = parser.parse((end_tag,))
        parser.delete_first_token()  # Remove the end tag
        return BlockBrickNode(brick_class, kwargs, nodelist)

    return tag_func


def register_brick_tags() -> None:
    """Register all bricks as template tags."""
    registry = get_registry()

    for name, brick_class in registry.items():
        # Skip if already registered
        if name in register.tags:
            continue

        if issubclass(brick_class, BlockBrick):
            tag_func = create_block_tag(brick_class)
        else:
            tag_func = create_simple_tag(brick_class)

        # Register the tag with Django's template library
        register.tag(name, tag_func)


# Note: We don't call register_brick_tags() here at import time
# because autodiscovery may not have run yet. Instead, we register
# tags in BrickAstleyConfig.ready() after autodiscovery completes.
