from django.apps import AppConfig


class BrickAstleyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "brickastley"
    verbose_name = "Brick Astley"

    def ready(self) -> None:
        from .autodiscover import autodiscover
        from .templatetags.brickastley import register_brick_tags

        autodiscover()
        register_brick_tags()
