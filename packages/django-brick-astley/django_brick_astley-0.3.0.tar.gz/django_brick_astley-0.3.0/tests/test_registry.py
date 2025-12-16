import pytest

from brickastley import Brick, register
from brickastley.registry import clear_registry, get_brick, get_registry


@pytest.fixture(autouse=True)
def clean_registry():
    """Clear registry before and after each test."""
    clear_registry()
    yield
    clear_registry()


class TestRegisterDecorator:
    """Tests for the @register decorator."""

    def test_register_without_arguments(self):
        """@register without arguments uses class name for tag name."""

        @register
        class MyButton(Brick):
            label: str

        registry = get_registry()
        assert "my_button" in registry
        assert registry["my_button"] is MyButton

    def test_register_with_custom_name(self):
        """@register(name="...") uses custom tag name."""

        @register(name="btn")
        class MyButton(Brick):
            label: str

        registry = get_registry()
        assert "btn" in registry
        assert "my_button" not in registry
        assert registry["btn"] is MyButton

    def test_register_sets_brick_name(self):
        """@register(name="...") also sets brick_name on class."""

        @register(name="btn")
        class MyButton(Brick):
            label: str

        assert MyButton.get_brick_name() == "btn"

    def test_register_returns_class(self):
        """@register returns the original class unchanged."""

        @register
        class MyButton(Brick):
            label: str

        assert MyButton.__name__ == "MyButton"
        assert issubclass(MyButton, Brick)

    def test_duplicate_registration_same_class(self):
        """Registering the same class twice is allowed."""

        @register
        class MyButton(Brick):
            label: str

        # Re-registering same class should not raise
        register(MyButton)

        registry = get_registry()
        assert registry["my_button"] is MyButton

    def test_duplicate_registration_different_class_raises(self):
        """Registering different class with same name raises."""

        @register
        class MyButton(Brick):
            label: str

        with pytest.raises(ValueError) as exc_info:

            @register(name="my_button")
            class AnotherButton(Brick):
                text: str

        assert "already registered" in str(exc_info.value)


class TestGetBrick:
    """Tests for get_brick function."""

    def test_get_existing_brick(self):
        """get_brick returns registered brick."""

        @register
        class MyButton(Brick):
            label: str

        result = get_brick("my_button")
        assert result is MyButton

    def test_get_nonexistent_brick(self):
        """get_brick returns None for unknown brick."""
        result = get_brick("nonexistent")
        assert result is None


class TestClearRegistry:
    """Tests for clear_registry function."""

    def test_clear_removes_all(self):
        """clear_registry removes all registered bricks."""

        @register
        class Button1(Brick):
            label: str

        @register
        class Button2(Brick):
            label: str

        assert len(get_registry()) == 2

        clear_registry()

        assert len(get_registry()) == 0
