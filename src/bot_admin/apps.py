"""Main class Bot Admin"""

from django.apps import AppConfig


class SbaAdminConfig(AppConfig):
    """SbaAdminConfig"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "bot_admin"
    module = "bot_admin"
