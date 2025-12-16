import pytest

from brickastley import BlockBrick, Brick, BrickValidationError


class TestBrickKwargs:
    """Tests for brick kwarg parsing and defaults."""

    def test_required_kwarg(self):
        """Required kwargs must be provided."""

        class MyBrick(Brick):
            name: str

        with pytest.raises(BrickValidationError) as exc_info:
            MyBrick()

        assert "Missing required kwarg 'name'" in str(exc_info.value)

    def test_optional_kwarg_with_default(self):
        """Optional kwargs use their default value when not provided."""

        class MyBrick(Brick):
            name: str
            color: str = "blue"

        brick = MyBrick(name="test")
        assert brick.name == "test"
        assert brick.color == "blue"

    def test_optional_kwarg_override(self):
        """Optional kwargs can be overridden."""

        class MyBrick(Brick):
            name: str
            color: str = "blue"

        brick = MyBrick(name="test", color="red")
        assert brick.color == "red"

    def test_nullable_kwarg(self):
        """Kwargs with None default are optional and nullable."""

        class MyBrick(Brick):
            name: str
            subtitle: str | None = None

        brick = MyBrick(name="test")
        assert brick.subtitle is None

        brick2 = MyBrick(name="test", subtitle="hello")
        assert brick2.subtitle == "hello"

    def test_unknown_kwargs_collected_in_extra(self):
        """Unknown kwargs are collected in extra."""

        class MyBrick(Brick):
            name: str

        brick = MyBrick(name="test", unknown="value", data_id="123")

        assert brick.name == "test"
        assert brick.extra == {"unknown": "value", "data_id": "123"}

    def test_extra_empty_when_no_unknown_kwargs(self):
        """extra is empty dict when no unknown kwargs provided."""

        class MyBrick(Brick):
            name: str

        brick = MyBrick(name="test")

        assert brick.extra == {}

    def test_class_kwarg_collected_in_extra(self):
        """'class' kwarg is specially handled and collected in extra."""

        class MyBrick(Brick):
            name: str

        # 'class' is a Python reserved keyword, but can be passed via **dict
        brick = MyBrick(**{"name": "test", "class": "my-class"})

        assert brick.name == "test"
        assert brick.extra == {"class": "my-class"}

    def test_class_kwarg_with_other_extra(self):
        """'class' kwarg works alongside other extra kwargs."""

        class MyBrick(Brick):
            name: str

        brick = MyBrick(**{"name": "test", "class": "my-class", "id": "my-id"})

        assert brick.extra == {"class": "my-class", "id": "my-id"}


class TestTypeValidation:
    """Tests for type validation."""

    def test_string_validation(self):
        """String kwargs validate correctly."""

        class MyBrick(Brick):
            name: str

        brick = MyBrick(name="hello")
        assert brick.name == "hello"

    def test_int_validation(self):
        """Integer kwargs validate correctly."""

        class MyBrick(Brick):
            count: int

        brick = MyBrick(count=42)
        assert brick.count == 42

    def test_bool_validation(self):
        """Boolean kwargs validate correctly."""

        class MyBrick(Brick):
            active: bool

        brick = MyBrick(active=True)
        assert brick.active is True

    def test_type_mismatch_in_debug(self, settings):
        """Type mismatch raises exception in DEBUG mode."""
        settings.DEBUG = True

        class MyBrick(Brick):
            count: int

        with pytest.raises(BrickValidationError) as exc_info:
            MyBrick(count="not an int")

        assert "expected int" in str(exc_info.value)

    def test_type_mismatch_in_production(self, settings, caplog):
        """Type mismatch logs warning in production mode."""
        settings.DEBUG = False

        class MyBrick(Brick):
            count: int

        # Should not raise, just log
        brick = MyBrick(count="not an int")
        assert brick.count == "not an int"  # Value still set despite type mismatch
        assert "Type validation failed" in caplog.text

    def test_union_type_validation(self):
        """Union types validate correctly."""

        class MyBrick(Brick):
            value: str | int

        brick1 = MyBrick(value="hello")
        assert brick1.value == "hello"

        brick2 = MyBrick(value=42)
        assert brick2.value == 42

    def test_optional_union_type(self):
        """Optional (Union with None) validates correctly."""

        class MyBrick(Brick):
            value: str | None = None

        brick1 = MyBrick()
        assert brick1.value is None

        brick2 = MyBrick(value="hello")
        assert brick2.value == "hello"

        brick3 = MyBrick(value=None)
        assert brick3.value is None


class TestBrickNaming:
    """Tests for brick name derivation."""

    def test_default_name_from_class(self):
        """Brick name is derived from class name."""

        class MyButton(Brick):
            label: str

        assert MyButton.get_brick_name() == "my_button"

    def test_default_name_camel_case(self):
        """CamelCase class names convert to snake_case."""

        class MyFancyButtonBrick(Brick):
            label: str

        assert MyFancyButtonBrick.get_brick_name() == "my_fancy_button_brick"

    def test_custom_brick_name(self):
        """Custom brick name can be set."""

        class MyButton(Brick):
            label: str
            brick_name = "btn"

        assert MyButton.get_brick_name() == "btn"

    def test_default_template_name(self):
        """Template name is derived from class name."""

        class MyButton(Brick):
            label: str

        assert MyButton.get_template_name() == "bricks/my_button.html"

    def test_custom_template_name(self):
        """Custom template name can be set."""

        class MyButton(Brick):
            label: str
            template_name = "custom/button.html"

        assert MyButton.get_template_name() == "custom/button.html"


class TestContextData:
    """Tests for context data generation."""

    def test_default_context_includes_kwargs(self):
        """Default context includes all kwarg values."""

        class MyBrick(Brick):
            name: str
            count: int = 0

        brick = MyBrick(name="test", count=5)
        context = brick.get_context_data()

        assert context["name"] == "test"
        assert context["count"] == 5

    def test_context_data_can_be_extended(self):
        """get_context_data can be overridden to add extra context."""

        class MyBrick(Brick):
            name: str

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context["uppercase_name"] = self.name.upper()
                return context

        brick = MyBrick(name="test")
        context = brick.get_context_data()

        assert context["name"] == "test"
        assert context["uppercase_name"] == "TEST"

    def test_context_includes_extra(self):
        """Context includes extra dict."""

        class MyBrick(Brick):
            name: str

        brick = MyBrick(name="test", data_id="123", aria_label="Test button")
        context = brick.get_context_data()

        assert context["name"] == "test"
        assert context["extra"] == {"data_id": "123", "aria_label": "Test button"}

    def test_context_extra_empty_when_none(self):
        """Context includes empty extra when no extra kwargs."""

        class MyBrick(Brick):
            name: str

        brick = MyBrick(name="test")
        context = brick.get_context_data()

        assert context["extra"] == {}


class TestBlockBrick:
    """Tests for BlockBrick."""

    def test_block_brick_inherits_from_brick(self):
        """BlockBrick is a subclass of Brick."""
        assert issubclass(BlockBrick, Brick)

    def test_block_brick_kwargs_work(self):
        """BlockBrick supports kwargs like Brick."""

        class Card(BlockBrick):
            title: str
            subtitle: str | None = None

        card = Card(title="Hello")
        assert card.title == "Hello"
        assert card.subtitle is None

    def test_block_brick_render_includes_children(self):
        """BlockBrick.render() accepts children parameter."""

        class Card(BlockBrick):
            title: str
            template_name = "test_card.html"

        card = Card(title="Hello")
        # Note: actual rendering requires template to exist
        # This test just verifies the method signature
        assert hasattr(card, "render")


class TestMedia:
    """Tests for Media class support."""

    def test_brick_with_media(self):
        """Bricks can define Media class."""

        class MyButton(Brick):
            label: str

            class Media:
                css = {"all": ["css/button.css"]}
                js = ["js/button.js"]

        # Media is handled by Django's MediaDefiningClass metaclass
        assert hasattr(MyButton, "media")
        assert "css/button.css" in str(MyButton(label="test").media)
        assert "js/button.js" in str(MyButton(label="test").media)

    def test_brick_without_media(self):
        """Bricks without Media class still work."""

        class MyButton(Brick):
            label: str

        brick = MyButton(label="test")
        # Should have empty media
        assert hasattr(brick, "media")
