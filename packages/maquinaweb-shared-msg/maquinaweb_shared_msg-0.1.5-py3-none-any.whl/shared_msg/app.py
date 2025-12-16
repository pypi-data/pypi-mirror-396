from django.apps import AppConfig


class SharedMsgConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shared_msg"

    def ready(self):
        from . import models  # noqa
