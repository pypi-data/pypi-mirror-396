"""
brickastley - Reusable bricks for Django templates
"""

__version__ = "0.1.0"

default_app_config = "brickastley.apps.BrickAstleyConfig"

from .brick import BlockBrick, Brick, BrickValidationError
from .registry import register

__all__ = [
    "Brick",
    "BlockBrick",
    "BrickValidationError",
    "register",
]
