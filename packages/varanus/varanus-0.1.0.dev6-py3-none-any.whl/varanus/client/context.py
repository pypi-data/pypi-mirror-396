import inspect
import logging
import sys
from contextvars import ContextVar, Token
from datetime import timedelta
from typing import TYPE_CHECKING

from ..events import Context, Error, Log, Metric, Request, now

if TYPE_CHECKING:
    from .client import VaranusClient

ONE_MS = timedelta(milliseconds=1)


class VaranusContext:
    """
    Shared public interface for how clients add logs/errors/metrics/etc. to Varanus.
    """

    request: Request | None

    def __init__(self, client: "VaranusClient", name, tags: dict | None = None):
        self.client = client
        self.name = name
        self.logs = []
        self.errors = []
        self.metrics: dict[str, Metric] = {}
        self.queries = []
        self.subcontexts = []
        self.tags = tags or {}
        self.request = None

    def build(self):
        return Context(
            timestamp=self.started,
            tags=self.tags,
            name=self.name,
            elapsed_ms=self.elapsed_ms,
            request=self.request,
            logs=self.logs,
            errors=self.errors,
            metrics=list(self.metrics.values()),
            queries=self.queries,
            subcontexts=[ctx.build() for ctx in self.subcontexts],
        )

    def should_send(self):
        if self.client.send_all:
            return True
        if self.logs or self.errors or self.metrics or self.queries:
            return True
        for ctx in self.subcontexts:
            if ctx.should_send():
                return True
        return False

    def __enter__(self):
        self.token = current_context.set(self)
        self.started = now()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.raw_exception((exc_type, exc_value, traceback))
        self.elapsed_ms = (now() - self.started) // ONE_MS
        current_context.reset(self.token)
        if self.token.old_value is Token.MISSING and self.should_send():
            # We're the bottom of the stack, build and send the event.
            try:
                self.client.send(self.build())
            except Exception as e:
                import traceback

                traceback.print_exception(e)

    def __setitem__(self, name, value):
        self.tags[name] = value

    def log(
        self,
        level: int,
        message: str,
        *args,
        exc_info=None,
        stacklevel: int = 1,
        tags: dict | None = None,
        **kwargs,
    ):
        frame = inspect.stack()[stacklevel]
        self.logs.append(
            Log(
                tags=tags or {},
                message=message % args,
                name=self.client.logger_name,
                level=level,
                file=frame.filename,
                lineno=frame.lineno,
                error=Error.from_exception(exc_info),
            )
        )

    def debug(self, message: str, *args, **kwargs):
        kwargs.setdefault("stacklevel", 2)
        self.log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        kwargs.setdefault("stacklevel", 2)
        self.log(logging.INFO, message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        kwargs.setdefault("stacklevel", 2)
        self.log(logging.WARNING, message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        kwargs.setdefault("stacklevel", 2)
        self.log(logging.ERROR, message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        kwargs.setdefault("stacklevel", 2)
        self.log(logging.CRITICAL, message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        kwargs.setdefault("stacklevel", 2)
        kwargs.setdefault("exc_info", sys.exc_info())
        self.log(logging.ERROR, message, *args, **kwargs)

    def raw_exception(self, exception, tags: dict | None = None):
        if err := Error.from_exception(exception, tags=tags):
            self.errors.append(err)

    def context(self, name: str = "", tags: dict | None = None):
        ctx = VaranusContext(self.client, name, tags)
        self.subcontexts.append(ctx)
        return ctx

    def metric(self, name: str, value: float = 0.0, tags: dict | None = None):
        if name not in self.metrics:
            self.metrics[name] = Metric(name=name, tags=tags or {})
        self.metrics[name].update(value)


current_context: ContextVar[VaranusContext | None] = ContextVar(
    "current_context",
    default=None,
)
