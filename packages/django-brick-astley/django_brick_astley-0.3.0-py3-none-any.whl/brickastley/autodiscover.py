from __future__ import annotations

from django.utils.module_loading import autodiscover_modules


def autodiscover() -> None:
    """
    Auto-discover bricks.py modules in all installed Django apps.

    This function imports bricks.py modules from all installed apps,
    triggering the @register decorators which populate the brick registry.
    """
    autodiscover_modules("bricks")
