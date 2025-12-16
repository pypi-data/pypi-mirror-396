import inspect
import logging
from datetime import datetime, timezone

from msgspec import Struct, field

from .utils import safe_repr


def now():
    return datetime.now(tz=timezone.utc)


class Event(Struct, kw_only=True, omit_defaults=True):
    timestamp: datetime = field(default_factory=now)
    tags: dict[str, str] = {}


class NodeInfo(Struct):
    name: str
    platform: str
    language: str
    language_version: str
    framework: str
    framework_version: str
    packages: dict[str, str]
    settings: dict[str, str]
    environment: dict[str, str]


class StackLine(Struct):
    file: str | None
    lineno: int | None
    function: str | None
    module: str | None
    linesrc: str | None
    locals: dict[str, str]


def capture_stack(skip: int = 0, include_locals: bool = False) -> list[StackLine]:
    lines = []
    for frame in inspect.stack()[skip + 1 :]:
        lines.append(
            StackLine(
                file=frame.filename,
                lineno=frame.lineno,
                linesrc=frame.code_context[0].strip() if frame.code_context else "",
                function=frame.function,
                module=frame.frame.f_globals.get("__name__", ""),
                locals=(
                    {name: safe_repr(val) for name, val in frame.frame.f_locals.items()}
                    if include_locals
                    else {}
                ),
            )
        )
    return lines


class Error(Event):
    kind: str
    module: str
    message: str
    stack: list[StackLine] = []

    @classmethod
    def from_exception(cls, exc_info, tags=None):
        if isinstance(exc_info, BaseException):
            exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
        if not exc_info or exc_info[0] is None:
            return None
        kind = exc_info[0].__name__
        message = str(exc_info[1])
        tb = exc_info[2]
        lines = []
        module = ""
        while tb:
            f_locals = getattr(tb.tb_frame, "f_locals", {})
            f_globals = getattr(tb.tb_frame, "f_globals", {})
            f_code = getattr(tb.tb_frame, "f_code", None)
            abs_path = f_code.co_filename if f_code else None
            function = f_code.co_name if f_code else None
            lineno = getattr(tb, "tb_lineno", None)
            linesrc = None
            if f_code and lineno:
                try:
                    source, start = inspect.getsourcelines(f_code)
                    linesrc = source[lineno - start].strip()
                except (OSError, TypeError):
                    pass
            module = f_globals.get("__name__", "")
            lines.append(
                StackLine(
                    file=abs_path,
                    lineno=lineno,
                    function=function,
                    module=module,
                    linesrc=linesrc,
                    locals={name: safe_repr(val) for name, val in f_locals.items()},
                )
            )
            tb = tb.tb_next
        return cls(
            tags=tags or {},
            kind=kind,
            module=module,
            message=message,
            stack=lines,
        )


class Log(Event):
    message: str
    name: str | None = None
    level: int | None = None
    file: str | None = None
    lineno: int | None = None
    error: Error | None = None

    @classmethod
    def from_string(
        cls,
        s: str,
        level: int | None = None,
        name: str | None = None,
        tags: dict | None = None,
    ):
        return cls(
            tags=tags or {},
            message=s,
            name=name,
            level=level,
            file=None,
            lineno=None,
            error=None,
        )

    @classmethod
    def from_logrecord(cls, record: logging.LogRecord, tags: dict | None = None):
        return cls(
            tags=tags or {},
            message=record.getMessage(),
            name=record.name,
            level=record.levelno,
            file=record.pathname,
            lineno=record.lineno,
            error=Error.from_exception(record.exc_info),
        )


class Metric(Event):
    name: str
    agg_count: int = 0
    agg_sum: float = 0.0
    agg_avg: float = 0.0
    agg_min: float = 0.0
    agg_max: float = 0.0

    def update(self, value: float):
        self.agg_count += 1
        self.agg_sum += value
        self.agg_avg = self.agg_sum / self.agg_count
        self.agg_min = min(self.agg_min, value)
        self.agg_max = max(self.agg_max, value)
        return self


class Query(Event):
    sql: str
    params: list[str]
    db: str
    elapsed_ms: int
    success: bool
    stack: list[StackLine] = []


class Request(Event):
    host: str
    method: str
    path: str
    query: str
    status: int
    headers: dict = {}
    size: int | None = None
    ip: str | None = None
    user: str | None = None


class Context(Event):
    name: str
    elapsed_ms: int
    request: Request | None = None
    errors: list[Error] = []
    logs: list[Log] = []
    metrics: list[Metric] = []
    queries: list[Query] = []
    subcontexts: list["Context"] = []
