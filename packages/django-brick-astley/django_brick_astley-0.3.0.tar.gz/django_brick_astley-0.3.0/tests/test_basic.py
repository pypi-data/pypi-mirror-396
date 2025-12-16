import pytest
from django.test import TestCase


class BasicTestCase(TestCase):
    """Basic tests for the brickastley package."""

    def test_app_config(self):
        """Test that the app is properly configured."""
        from django.apps import apps

        app_config = apps.get_app_config("brickastley")
        assert app_config.name == "brickastley"
        assert app_config.verbose_name == "Brick Astley"
