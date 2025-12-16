import os
import platform
from importlib.metadata import distributions
from typing import Iterable
from urllib.parse import urlsplit

from varanus.events import Context, NodeInfo

from ..utils import import_string
from .context import VaranusContext, current_context
from .loggers import QueryLogger
from .transport.base import BaseTransport


def install_query_logger(logger):
    def handler(sender, **kwargs):
        if logger not in kwargs["connection"].execute_wrappers:
            kwargs["connection"].execute_wrappers.append(logger)

    return handler


def resolve_include_exclude(
    items: Iterable[str],
    include: Iterable[str] | bool,
    exclude: Iterable[str] | None,
) -> set[str]:
    if not include:
        return set()

    if include is True:
        resolved = set(items)
    else:
        resolved = set(items).intersection(include)

    if exclude is not None:
        resolved.difference_update(exclude)

    return resolved


class VaranusClient:
    # Things we don't want to send, at least by default.
    sensitive_headers = set(["authorization", "cookie", "proxy-authorization"])
    sensitive_settings = set(["SECRET_KEY"])
    sensitive_env = set(["PGPASSWORD"])

    scheme_transports = {
        "http": "varanus.client.transport.http.ThreadedHttpTransport",
        "https": "varanus.client.transport.http.ThreadedHttpTransport",
        "db": "varanus.client.transport.database.ModelTransport",
    }

    configured = False

    def setup(
        self,
        dsn: str,
        environment: str,
        node: str | None = None,
        transport_class: str | type[BaseTransport] | None = None,
        request_attr: str = "varanus",
        logger_name: str = "varanus.request",
        tags: dict | None = None,
        include_headers: Iterable[str] | bool = False,
        exclude_headers: Iterable[str] | None = None,
        include_settings: Iterable[str] | bool = True,
        exclude_settings: Iterable[str] | None = None,
        include_default_settings: bool = False,
        filter_settings: bool = True,
        include_env: Iterable[str] | bool = False,
        exclude_env: Iterable[str] | None = None,
        log_queries: bool | int = False,
        log_query_params: bool = False,
        log_query_stack: bool = False,
        query_metrics: bool | str = False,
        send_all: bool = False,
        install: list | None = None,
    ):
        url = urlsplit(dsn)
        self.environment = environment
        self.node = node or platform.node()
        if transport_class is None:
            if url.scheme not in self.scheme_transports:
                raise ValueError(f"No transport class found for `{url.scheme}`")
            resolved_class = import_string(self.scheme_transports[url.scheme])
        elif isinstance(transport_class, str):
            resolved_class = import_string(transport_class)
        else:
            resolved_class = transport_class
        if not issubclass(resolved_class, BaseTransport):
            raise ValueError(
                f"Transport class `{transport_class}` must be a subclass of"
                "BaseTransport."
            )
        self.transport = resolved_class(url, self.environment, self.node)
        self.request_attr = request_attr
        self.logger_name = logger_name
        self.tags = tags or {}
        self.include_headers = include_headers
        self.exclude_headers = (
            self.sensitive_headers if exclude_headers is None else set(exclude_headers)
        )
        self.include_settings = include_settings
        self.exclude_settings = (
            self.sensitive_settings
            if exclude_settings is None
            else set(exclude_settings)
        )
        self.include_default_settings = include_default_settings
        self.filter_settings = filter_settings
        self.include_env = include_env
        self.exclude_env = (
            self.sensitive_env if exclude_env is None else set(exclude_env)
        )
        if log_queries or query_metrics:
            try:
                # The logger is installed as early as possible, and for all connections.
                from django.db.backends.signals import connection_created

                # Create a single QueryLogger to be used by all connections.
                self.query_logger = QueryLogger(
                    log_queries,
                    log_query_params,
                    log_query_stack,
                    query_metrics,
                )
                # Install it in each new connection (if it's not already installed).
                connection_created.connect(
                    install_query_logger(self.query_logger),
                    weak=False,
                )
            except ImportError:
                pass
        self.send_all = send_all
        self.configured = True
        if install:
            if "django.contrib.auth.middleware.AuthenticationMiddleware" in install:
                idx = install.index(
                    "django.contrib.auth.middleware.AuthenticationMiddleware"
                )
                install.insert(idx + 1, "varanus.client.middleware.VaranusMiddleware")
            elif "django.middleware.common.CommonMiddleware" in install:
                idx = install.index("django.middleware.common.CommonMiddleware")
                install.insert(idx + 1, "varanus.client.middleware.VaranusMiddleware")
            else:
                install.append("varanus.client.middleware.VaranusMiddleware")
        return self

    def send(self, *events: Context):
        for e in events:
            self.transport.send(e)

    def ping(self):
        from django import get_version
        from django.conf import settings

        if self.filter_settings:
            from django.views.debug import SafeExceptionReporterFilter

            settings_dict = {
                k: repr(v)
                for k, v in SafeExceptionReporterFilter().get_safe_settings().items()
            }
        else:
            settings_dict = {
                s: repr(getattr(settings, s)) for s in dir(settings) if s.isupper()
            }

        include_settings = resolve_include_exclude(
            settings_dict.keys(),
            self.include_settings,
            self.exclude_settings,
        )
        include_env = resolve_include_exclude(
            os.environ.keys(),
            self.include_env,
            self.exclude_env,
        )

        self.transport.ping(
            NodeInfo(
                name=self.node,
                platform=platform.platform(),
                language=platform.python_implementation(),
                language_version=platform.python_version(),
                framework="Django",
                framework_version=get_version(),
                packages={d.name: d.version for d in distributions()},
                settings={
                    s: settings_dict[s]
                    for s in include_settings
                    if self.include_default_settings or settings.is_overridden(s)
                },
                environment={e: os.environ[e] for e in include_env},
            )
        )

    def log(self, level: int, message: str, *args, **kwargs):
        if ctx := current_context.get():
            kwargs.setdefault("stacklevel", 2)
            ctx.log(level, message, *args, **kwargs)

    def raw_exception(self, exception, tags: dict | None = None):
        if ctx := current_context.get():
            ctx.raw_exception(exception, tags=tags)

    def metric(self, name: str, value: float = 0.0, tags: dict | None = None):
        if ctx := current_context.get():
            ctx.metric(name, value, tags=tags)

    def context(self, name: str, tags: dict | None = None):
        if ctx := current_context.get():
            return ctx.context(name, tags)
        else:
            return VaranusContext(self, name, tags or self.tags)


client = VaranusClient()
