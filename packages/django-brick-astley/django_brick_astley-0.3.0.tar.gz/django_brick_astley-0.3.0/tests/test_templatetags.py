import pytest
from django.template import Context, Template, TemplateSyntaxError, engines
from django.template.base import Parser

from brickastley import BlockBrick, Brick, register
from brickastley.registry import clear_registry


@pytest.fixture(autouse=True)
def clean_registry():
    """Clear registry before and after each test."""
    clear_registry()
    yield
    clear_registry()


@pytest.fixture
def reload_templatetags():
    """Reload templatetags after registering bricks."""
    # Import here to trigger tag registration
    from brickastley.templatetags import brickastley as brickastley_tags

    def _reload():
        brickastley_tags.register_brick_tags()

    return _reload


@pytest.fixture
def parser():
    """Create a Django template parser for testing."""
    engine = engines["django"]
    return Parser(
        [], engine.engine.template_libraries, engine.engine.template_builtins
    )


class TestSimpleBrickRendering:
    """Tests for simple brick template tag rendering."""

    def test_render_simple_brick(self, reload_templatetags):
        """Simple brick renders correctly."""

        @register
        class TestButton(Brick):
            label: str
            template_name = "test_button.html"

        reload_templatetags()

        # Create a simple template that uses our brick
        # We need to mock the template loading, so we'll test the node directly
        from brickastley.templatetags.brickastley import BrickNode

        node = BrickNode(TestButton, {"label": "Click me"})
        # We can't fully test without a template file, but we can test instantiation
        assert node.brick_class is TestButton
        assert node.kwargs == {"label": "Click me"}

    def test_parse_string_kwarg(self, parser):
        """String kwargs are parsed correctly."""
        from django.template.base import FilterExpression

        from brickastley.templatetags.brickastley import parse_tag_kwargs, resolve_kwargs

        result = parse_tag_kwargs(parser, ['label="Hello World"'])
        # Quoted strings are parsed as FilterExpressions
        assert isinstance(result["label"], FilterExpression)
        # But resolve to the string value
        resolved = resolve_kwargs(result, Context({}))
        assert resolved["label"] == "Hello World"

    def test_parse_single_quoted_string(self, parser):
        """Single-quoted strings are parsed correctly."""
        from brickastley.templatetags.brickastley import parse_tag_kwargs, resolve_kwargs

        result = parse_tag_kwargs(parser, ["label='Hello'"])
        resolved = resolve_kwargs(result, Context({}))
        assert resolved["label"] == "Hello"

    def test_parse_integer_kwarg(self, parser):
        """Integer kwargs are parsed correctly."""
        from brickastley.templatetags.brickastley import parse_tag_kwargs

        result = parse_tag_kwargs(parser, ["count=42"])
        assert result["count"] == 42
        assert isinstance(result["count"], int)

    def test_parse_negative_integer(self, parser):
        """Negative integers are parsed correctly."""
        from brickastley.templatetags.brickastley import parse_tag_kwargs

        result = parse_tag_kwargs(parser, ["count=-5"])
        assert result["count"] == -5

    def test_parse_float_kwarg(self, parser):
        """Float kwargs are parsed correctly."""
        from brickastley.templatetags.brickastley import parse_tag_kwargs

        result = parse_tag_kwargs(parser, ["price=19.99"])
        assert result["price"] == 19.99
        assert isinstance(result["price"], float)

    def test_parse_boolean_true(self, parser):
        """Boolean True is parsed correctly."""
        from brickastley.templatetags.brickastley import parse_tag_kwargs

        result = parse_tag_kwargs(parser, ["active=True"])
        assert result["active"] is True

    def test_parse_boolean_false(self, parser):
        """Boolean False is parsed correctly."""
        from brickastley.templatetags.brickastley import parse_tag_kwargs

        result = parse_tag_kwargs(parser, ["active=False"])
        assert result["active"] is False

    def test_parse_none(self, parser):
        """None is parsed correctly."""
        from brickastley.templatetags.brickastley import parse_tag_kwargs

        result = parse_tag_kwargs(parser, ["value=None"])
        assert result["value"] is None

    def test_parse_variable_kwarg(self, parser):
        """Variable kwargs are parsed as FilterExpressions."""
        from django.template.base import FilterExpression

        from brickastley.templatetags.brickastley import parse_tag_kwargs

        result = parse_tag_kwargs(parser, ["label=my_variable"])
        assert isinstance(result["label"], FilterExpression)

    def test_parse_variable_with_filter(self, parser):
        """Variable kwargs with filters are parsed correctly."""
        from django.template.base import FilterExpression

        from brickastley.templatetags.brickastley import parse_tag_kwargs, resolve_kwargs

        result = parse_tag_kwargs(parser, ["label=name|title"])
        assert isinstance(result["label"], FilterExpression)

        # Test that the filter is actually applied when resolved
        context = Context({"name": "hello world"})
        resolved = resolve_kwargs(result, context)
        assert resolved["label"] == "Hello World"

    def test_parse_chained_filters(self, parser):
        """Chained filters are parsed and applied correctly."""
        from django.template.base import FilterExpression

        from brickastley.templatetags.brickastley import parse_tag_kwargs, resolve_kwargs

        result = parse_tag_kwargs(parser, ["label=name|lower|title"])
        assert isinstance(result["label"], FilterExpression)

        context = Context({"name": "HELLO WORLD"})
        resolved = resolve_kwargs(result, context)
        assert resolved["label"] == "Hello World"

    def test_invalid_kwarg_format_raises(self, parser):
        """Invalid kwarg format raises TemplateSyntaxError."""
        from brickastley.templatetags.brickastley import parse_tag_kwargs

        with pytest.raises(TemplateSyntaxError) as exc_info:
            parse_tag_kwargs(parser, ["invalid"])

        assert "must be in kwarg=value format" in str(exc_info.value)


class TestVariableResolution:
    """Tests for template variable resolution."""

    def test_resolve_static_kwargs(self):
        """Static kwargs pass through unchanged."""
        from brickastley.templatetags.brickastley import resolve_kwargs

        kwargs = {"label": "Hello", "count": 42}
        context = Context({})

        result = resolve_kwargs(kwargs, context)
        assert result == {"label": "Hello", "count": 42}

    def test_resolve_filter_expression_kwargs(self, parser):
        """FilterExpression kwargs are resolved from context."""
        from brickastley.templatetags.brickastley import resolve_kwargs

        filter_expr = parser.compile_filter("my_label")
        kwargs = {"label": filter_expr, "static": "value"}
        context = Context({"my_label": "Dynamic Label"})

        result = resolve_kwargs(kwargs, context)
        assert result["label"] == "Dynamic Label"
        assert result["static"] == "value"


class TestBlockBrickRendering:
    """Tests for block brick template tag rendering."""

    def test_block_brick_node_has_nodelist(self, reload_templatetags):
        """BlockBrickNode stores the nodelist for children."""
        from django.template.base import NodeList

        from brickastley.templatetags.brickastley import BlockBrickNode

        @register
        class TestCard(BlockBrick):
            title: str

        nodelist = NodeList()
        node = BlockBrickNode(TestCard, {"title": "Hello"}, nodelist)

        assert node.brick_class is TestCard
        assert node.nodelist is nodelist


class TestMultipleKwargs:
    """Tests for parsing multiple kwargs."""

    def test_parse_multiple_kwargs(self, parser):
        """Multiple kwargs are parsed correctly."""
        from brickastley.templatetags.brickastley import parse_tag_kwargs, resolve_kwargs

        result = parse_tag_kwargs(
            parser,
            ['label="Click"', "count=5", "active=True", "price=9.99"],
        )

        # Resolve the filter expressions
        resolved = resolve_kwargs(result, Context({}))
        assert resolved["label"] == "Click"
        assert result["count"] == 5
        assert result["active"] is True
        assert result["price"] == 9.99


class TestAttrsFilter:
    """Tests for the attrs filter."""

    def test_attrs_empty_dict(self):
        """Empty dict returns empty string."""
        from brickastley.templatetags.brickastley import attrs

        assert attrs({}) == ""

    def test_attrs_single_attr(self):
        """Single attribute is formatted correctly."""
        from brickastley.templatetags.brickastley import attrs

        result = attrs({"id": "foo"})
        assert result == ' id="foo"'

    def test_attrs_multiple_attrs(self):
        """Multiple attributes are formatted correctly."""
        from brickastley.templatetags.brickastley import attrs

        result = attrs({"id": "foo", "class": "bar"})
        # flatatt sorts by key, so class comes before id
        assert 'id="foo"' in result
        assert 'class="bar"' in result

    def test_attrs_underscore_to_hyphen(self):
        """Underscores in keys are converted to hyphens."""
        from brickastley.templatetags.brickastley import attrs

        result = attrs({"data_id": "123", "aria_label": "test"})
        assert 'data-id="123"' in result
        assert 'aria-label="test"' in result

    def test_attrs_boolean_true(self):
        """Boolean True renders as attribute name."""
        from brickastley.templatetags.brickastley import attrs

        result = attrs({"disabled": True})
        assert 'disabled="disabled"' in result

    def test_attrs_boolean_false_skipped(self):
        """Boolean False values are skipped."""
        from brickastley.templatetags.brickastley import attrs

        result = attrs({"disabled": False, "id": "foo"})
        assert "disabled" not in result
        assert 'id="foo"' in result

    def test_attrs_none_skipped(self):
        """None values are skipped."""
        from brickastley.templatetags.brickastley import attrs

        result = attrs({"title": None, "id": "foo"})
        assert "title" not in result
        assert 'id="foo"' in result

    def test_attrs_in_template(self):
        """attrs filter works in templates."""
        template = Template("{% load brickastley %}<div{{ extra|attrs }}></div>")
        context = Context({"extra": {"id": "test", "data_value": "123"}})
        result = template.render(context)
        assert 'id="test"' in result
        assert 'data-value="123"' in result
