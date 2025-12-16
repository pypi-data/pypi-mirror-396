import logging
from typing import Any

from django.tasks import Task, TaskResult, TaskResultStatus
from django.tasks.backends.base import BaseTaskBackend
from django.tasks.exceptions import InvalidTask, TaskResultDoesNotExist
from django.tasks.signals import task_enqueued
from django.utils.json import normalize_json

from .models import ScheduledTask

logger = logging.getLogger(__name__)


class DatabaseBackend(BaseTaskBackend):
    supports_defer = True
    supports_get_result = True
    supports_priority = True

    @property
    def immediate(self):
        return bool(self.options.get("immediate", False))

    def validate_task(self, task):
        super().validate_task(task)
        if self.immediate and task.run_after is not None:
            raise InvalidTask("Backend does not support run_after in immediate mode.")

    def enqueue(self, task: Task, args: list[Any], kwargs: dict[str, Any]):
        self.validate_task(task)

        # Start immediate tasks at RUNNING so they don't get picked up by workers.
        scheduled = ScheduledTask.objects.create(
            status=(
                TaskResultStatus.RUNNING if self.immediate else TaskResultStatus.READY
            ),
            task_path=task.module_path,
            priority=task.priority,
            queue=task.queue_name,
            backend=task.backend,
            run_after=task.run_after,
            args=normalize_json(args),
            kwargs=normalize_json(kwargs),
        )

        result = scheduled.result
        task_enqueued.send(type(self), task_result=result)

        if self.immediate:
            logger.info(
                f"Running task {scheduled.pk} IMMEDIATELY ({scheduled.task_path})"
            )
            scheduled.run_and_update(start=True)
            result.refresh()

        return result

    def get_result(self, result_id) -> TaskResult:
        try:
            return ScheduledTask.objects.get(pk=result_id).result
        except ScheduledTask.DoesNotExist:
            raise TaskResultDoesNotExist(result_id)
