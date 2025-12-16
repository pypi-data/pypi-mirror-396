from __future__ import annotations

from typing import TYPE_CHECKING, Callable, TypeVar, overload

if TYPE_CHECKING:
    from .brick import Brick

B = TypeVar("B", bound="Brick")

# Global registry mapping brick names to brick classes
_registry: dict[str, type[Brick]] = {}


def get_registry() -> dict[str, type[Brick]]:
    """Get the global brick registry."""
    return _registry


def get_brick(name: str) -> type[Brick] | None:
    """Get a brick class by its registered name."""
    return _registry.get(name)


def clear_registry() -> None:
    """Clear the brick registry. Useful for testing."""
    _registry.clear()


@overload
def register(cls: type[B]) -> type[B]: ...


@overload
def register(
    cls: None = None, *, name: str | None = None
) -> Callable[[type[B]], type[B]]: ...


def register(
    cls: type[B] | None = None, *, name: str | None = None
) -> type[B] | Callable[[type[B]], type[B]]:
    """
    Register a brick class.

    Can be used as a decorator with or without arguments:

        @register
        class MyBrick(Brick):
            ...

        @register(name="custom_name")
        class MyBrick(Brick):
            ...

    Args:
        cls: The brick class to register (when used without parentheses)
        name: Optional custom name for the brick's template tag
    """

    def decorator(brick_cls: type[B]) -> type[B]:
        # Determine the brick name
        if name:
            brick_name = name
            # Also set it on the class so get_brick_name() returns it
            brick_cls.brick_name = name  # type: ignore[attr-defined]
        else:
            brick_name = brick_cls.get_brick_name()  # type: ignore[attr-defined]

        # Check for duplicate registration
        if brick_name in _registry:
            existing = _registry[brick_name]
            if existing is not brick_cls:
                raise ValueError(
                    f"Brick name '{brick_name}' is already registered "
                    f"by {existing.__module__}.{existing.__name__}"
                )

        _registry[brick_name] = brick_cls
        return brick_cls

    # Handle both @register and @register(...) syntax
    if cls is not None:
        return decorator(cls)
    return decorator
