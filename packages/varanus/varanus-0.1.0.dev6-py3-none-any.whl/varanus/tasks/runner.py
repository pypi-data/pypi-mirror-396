import concurrent.futures
import functools
import importlib
import logging
import platform
import threading
import time

from django.db import transaction
from django.db.models import Q
from django.tasks import DEFAULT_TASK_BACKEND_ALIAS, TaskResultStatus, task_backends
from django.utils import timezone
from django.utils.module_loading import import_string

from .models import ScheduledTask

logger = logging.getLogger(__name__)


def run_task(pk: str) -> TaskResultStatus:
    task = ScheduledTask.objects.get(pk=pk)
    logger.info(f"Running task {pk} ({task.task_path})")
    return task.run_and_update()


class Runner:
    def __init__(
        self,
        workers: int = 4,
        worker_id: str | None = None,
        backend: str = DEFAULT_TASK_BACKEND_ALIAS,
    ):
        self.workers = workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=workers)
        self.tasks: dict[str, concurrent.futures.Future] = {}
        self.seen_modules: set[str] = set()
        self.worker_id = worker_id or platform.node()
        self.backend = task_backends[backend]
        self.stopsign = threading.Event()
        self.lock = threading.Lock()

    def get_tasks(self, number: int):
        if number <= 0:
            return []
        with transaction.atomic(durable=True):
            now = timezone.now()
            tasks = list(
                ScheduledTask.objects.filter(
                    Q(run_after__isnull=True) | Q(run_after__lte=now),
                    status=TaskResultStatus.READY,
                    backend=self.backend.alias,
                    queue__in=self.backend.queues,
                )
                .order_by("-priority", "enqueued_at")[:number]
                .select_for_update()
            )
            for t in tasks:
                t.status = TaskResultStatus.RUNNING
                t.started_at = now
                # TODO: can't figure out how to do this in a .update call.
                t.worker_ids.append(self.worker_id)
                t.save(update_fields=["status", "started_at", "worker_ids"])
        return tasks

    def task_done(self, pk: str, fut: concurrent.futures.Future):
        with self.lock:
            del self.tasks[pk]
        try:
            status = fut.result()
            logger.info(f"Task {pk} finished with status {status}")
        except Exception as ex:
            logger.info(f"Task {pk} raised {ex}")

    def run(self):
        logger.info(f"Starting task runner with {self.workers} workers")
        try:
            while not self.stopsign.is_set():
                with self.lock:
                    available = max(0, self.workers - len(self.tasks))
                    for t in self.get_tasks(available):
                        # Keep track of task modules we've seen, so we can reload them
                        # when necessary.
                        self.seen_modules.add(t.task_path.rsplit(".", 1)[0])
                        f = self.executor.submit(run_task, t.task_id)
                        self.tasks[t.task_id] = f
                        f.add_done_callback(
                            functools.partial(self.task_done, t.task_id),
                        )  # type:ignore
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        self.executor.shutdown()

    def stop(self):
        logger.info("Shutting down task runner")
        self.stopsign.set()

    def reload(self):
        with self.lock:
            for mod_path in list(self.seen_modules):
                try:
                    mod = import_string(mod_path)
                    importlib.reload(mod)
                    logger.debug(f"Reloaded module {mod_path}")
                except ImportError:
                    logger.debug(f"Error reloading {mod_path}")
                    self.seen_modules.discard(mod_path)
