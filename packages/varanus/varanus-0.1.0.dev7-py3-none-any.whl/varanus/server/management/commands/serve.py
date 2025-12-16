import os
import threading

from django.conf import settings
from django.core.management import BaseCommand
from granian import Granian
from granian.constants import Interfaces


def cpus() -> int:
    return os.cpu_count() or 4


class Command(BaseCommand):
    help = "Web server and task runner."

    def add_arguments(self, parser):
        parser.add_argument("-r", "--reload", action="store_true", default=False)
        parser.add_argument("-w", "--workers", type=int, default=1)
        parser.add_argument("-t", "--threads", type=int, default=cpus())
        parser.add_argument(
            "-k",
            "--tasks",
            nargs="?",
            type=int,
            const=cpus() // 2,
            default=0,
        )

    def on_startup(self):
        if self.runner:
            threading.Thread(target=self.runner.run).start()

    def on_reload(self):
        if self.runner:
            self.runner.reload()

    def on_shutdown(self):
        if self.runner:
            self.runner.stop()

    def handle(self, *args, **options):
        self.runner = None
        if workers := options["tasks"]:
            from varanus.tasks.runner import Runner

            self.runner = Runner(workers=workers)

        server = Granian(
            ":".join(settings.WSGI_APPLICATION.rsplit(".", 1)),
            address="0.0.0.0",
            port=9000,
            interface=Interfaces.WSGI,
            workers=options["workers"],
            blocking_threads=options["threads"],
            log_access=True,
            reload=options["reload"],
            reload_paths=[settings.BASE_DIR / "src"],
            websockets=False,
        )
        server.on_startup(self.on_startup)
        server.on_reload(self.on_reload)
        server.on_shutdown(self.on_shutdown)
        server.serve()
