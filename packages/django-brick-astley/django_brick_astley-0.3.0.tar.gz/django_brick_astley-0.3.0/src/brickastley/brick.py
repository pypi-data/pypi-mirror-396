from __future__ import annotations

import logging
import re
from typing import Any, ClassVar, get_type_hints

from django.conf import settings
from django.forms.widgets import Media, MediaDefiningClass
from django.template import loader
from django.utils.functional import Promise

logger = logging.getLogger(__name__)


class BrickValidationError(Exception):
    """Raised when brick kwargs fail type validation."""

    pass


def _camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _validate_type(
    value: Any, expected_type: type, kwarg_name: str, brick_name: str | None = None
) -> None:
    """Validate that a value matches the expected type."""
    # Skip validation for Any type
    if expected_type is Any:
        return

    brick_context = f" in '{brick_name}' brick" if brick_name else ""
    # Handle None for optional types
    if value is None:
        # Check if None is allowed (Union with None or Optional)
        origin = getattr(expected_type, "__origin__", None)
        if origin is type(None):
            return
        # For Union types (including Optional), check if NoneType is in args
        if hasattr(expected_type, "__args__") and type(None) in expected_type.__args__:
            return
        raise BrickValidationError(
            f"kwarg '{kwarg_name}'{brick_context} received None but is not optional"
        )

    # Get the origin type for generic types (e.g., list[int] -> list)
    origin = getattr(expected_type, "__origin__", None)

    if origin is not None:
        # Handle Union types (including Optional)
        if hasattr(expected_type, "__args__"):
            # For Union, check if value matches any of the types
            import typing

            if origin is typing.Union:
                for arg in expected_type.__args__:
                    if arg is type(None):
                        continue
                    try:
                        _validate_type(value, arg, kwarg_name)
                        return  # Valid for at least one type
                    except BrickValidationError:
                        continue
                raise BrickValidationError(
                    f"kwarg '{kwarg_name}'{brick_context} expected {expected_type}, got {type(value).__name__}"
                )

        # For other generic types, just check the origin
        if not isinstance(value, origin):
            raise BrickValidationError(
                f"kwarg '{kwarg_name}'{brick_context} expected {expected_type}, got {type(value).__name__}"
            )
    else:
        # Simple type check
        # Accept Django lazy translation objects (Promise) for str types.
        # Check for str-specific method 'upper' to ensure it's a lazy string, not lazy list etc.
        if expected_type is str and isinstance(value, Promise) and hasattr(value, "upper"):
            return
        if not isinstance(value, expected_type):
            raise BrickValidationError(
                f"kwarg '{kwarg_name}'{brick_context} expected {expected_type.__name__}, got {type(value).__name__}"
            )


class BrickMeta(MediaDefiningClass):
    """
    Metaclass for Brick that processes kwarg definitions.

    Inherits from MediaDefiningClass to support the Media inner class
    pattern used by Django forms and widgets.
    """

    def __new__(
        mcs, name: str, bases: tuple, namespace: dict, **kwargs: Any
    ) -> BrickMeta:
        cls = super().__new__(mcs, name, bases, namespace)

        # Skip processing for base classes
        if name in ("Brick", "BlockBrick"):
            return cls

        # Gather kwargs from type hints
        hints = {}
        defaults = {}

        # Collect from parent classes first
        for base in reversed(cls.__mro__):
            if hasattr(base, "__annotations__"):
                for kwarg_name, kwarg_type in base.__annotations__.items():
                    # Skip class variables and private attributes
                    if kwarg_name.startswith("_"):
                        continue
                    if hasattr(base, "__class_kwargs__"):
                        continue
                    hints[kwarg_name] = kwarg_type
                    # Check for default value
                    if hasattr(base, kwarg_name):
                        defaults[kwarg_name] = getattr(base, kwarg_name)

        # Filter out ClassVar kwargs and known class attributes
        class_attrs = {"template_name", "brick_name"}
        cls.__brick_kwargs__ = {k: v for k, v in hints.items() if k not in class_attrs}
        cls.__brick_defaults__ = {
            k: v for k, v in defaults.items() if k not in class_attrs
        }

        return cls


class Brick(metaclass=BrickMeta):
    """
    Base class for simple (self-closing) bricks.

    Usage:
        @register
        class MyButton(Brick):
            label: str
            variant: str = "primary"

            class Media:
                css = {"all": ["css/button.css"]}
                js = ["js/button.js"]

    Template tag: {% my_button label="Click me" %}
    Template: bricks/my_button.html

    The Media class works exactly like Django forms/widgets Media.
    """

    # Can be overridden by subclasses
    template_name: ClassVar[str | None] = None
    brick_name: ClassVar[str | None] = None

    # Set by metaclass
    __brick_kwargs__: ClassVar[dict[str, type]]
    __brick_defaults__: ClassVar[dict[str, Any]]

    def __init__(self, **kwargs: Any) -> None:
        self._validate_and_set_kwargs(kwargs)

    def _validate_and_set_kwargs(self, kwargs: dict[str, Any]) -> None:
        """Validate kwargs against kwarg definitions and set as attributes."""
        brick_kwargs = self.__brick_kwargs__
        defaults = self.__brick_defaults__

        # Check for required kwargs
        for kwarg_name in brick_kwargs:
            if kwarg_name not in kwargs and kwarg_name not in defaults:
                raise BrickValidationError(
                    f"Missing required kwarg '{kwarg_name}' for brick "
                    f"'{self.__class__.__name__}'"
                )

        # Collect extra kwargs not defined in the brick class
        self.extra: dict[str, Any] = {}

        # Handle 'class' specially since it's a Python reserved keyword.
        # Users can pass class="foo" in templates and it will be available
        # in extra["class"].
        if "class" in kwargs:
            self.extra["class"] = kwargs.pop("class")

        # Validate and set each kwarg
        for kwarg_name, value in kwargs.items():
            if kwarg_name not in brick_kwargs:
                # Collect unknown kwargs in extra
                self.extra[kwarg_name] = value
                continue

            expected_type = brick_kwargs[kwarg_name]
            try:
                _validate_type(
                    value, expected_type, kwarg_name, self.__class__.__name__
                )
            except BrickValidationError:
                if getattr(settings, "DEBUG", False):
                    raise
                else:
                    logger.warning(
                        f"Type validation failed for kwarg '{kwarg_name}' in "
                        f"brick '{self.__class__.__name__}': expected "
                        f"{expected_type}, got {type(value).__name__}"
                    )

            setattr(self, kwarg_name, value)

        # Set defaults for missing optional kwargs
        for kwarg_name, default in defaults.items():
            if kwarg_name not in kwargs:
                setattr(self, kwarg_name, default)

    @classmethod
    def get_brick_name(cls) -> str:
        """Get the template tag name for this brick."""
        if cls.brick_name:
            return cls.brick_name
        return _camel_to_snake(cls.__name__)

    @classmethod
    def get_template_name(cls) -> str:
        """Get the template path for this brick."""
        if cls.template_name:
            return cls.template_name
        return f"bricks/{_camel_to_snake(cls.__name__)}.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Get the template context for rendering.

        Override this method to customize the context passed to the template.
        By default, returns all brick kwargs as context variables, plus
        extra containing any additional kwargs not defined in the class.
        """
        context = {}
        for kwarg_name in self.__brick_kwargs__:
            if hasattr(self, kwarg_name):
                context[kwarg_name] = getattr(self, kwarg_name)
        context["extra"] = self.extra
        context.update(kwargs)
        return context

    def render(self, context: dict[str, Any] | None = None) -> str:
        """Render the brick to a string.

        Args:
            context: Optional parent template context. If provided, brick
                variables are merged on top, giving access to request and
                other context processor variables.
        """
        tpl = loader.get_template(self.get_template_name())
        brick_context = self.get_context_data()
        if context is not None:
            full_context = {**context, **brick_context}
        else:
            full_context = brick_context
        return tpl.render(full_context)


class BlockBrick(Brick):
    """
    Base class for block bricks that can wrap children.

    Usage:
        @register
        class Card(BlockBrick):
            title: str

    Template tag:
        {% card title="Hello" %}
            <p>Card content here</p>
        {% endcard %}

    Template (bricks/card.html):
        <div class="card">
            <h2>{{ title }}</h2>
            <div class="card-body">
                {{ children }}
            </div>
        </div>
    """

    def render(
        self, children: str = "", context: dict[str, Any] | None = None
    ) -> str:
        """Render the brick with children content.

        Args:
            children: Rendered content from the block's child nodes.
            context: Optional parent template context. If provided, brick
                variables are merged on top, giving access to request and
                other context processor variables.
        """
        tpl = loader.get_template(self.get_template_name())
        brick_context = self.get_context_data(children=children)
        if context is not None:
            full_context = {**context, **brick_context}
        else:
            full_context = brick_context
        return tpl.render(full_context)
