from django.apps import AppConfig


class VaranusServer(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "varanus.server"
    label = "varanus"

    def ready(self):
        pass
