from django.apps import AppConfig


class VaranusClient(AppConfig):
    name = "varanus.client"

    def ready(self):
        pass
