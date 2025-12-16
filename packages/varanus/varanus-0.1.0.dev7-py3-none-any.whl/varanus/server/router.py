import contextlib
from contextvars import ContextVar

from django.conf import settings
from django.db import connections

active_schema: ContextVar[str] = ContextVar("active_schema")


def set_search_path(schema, conn=None):
    if conn is None:
        conn = connections[settings.VARANUS_DB_ALIAS]
    if not settings.VARANUS_USE_SCHEMAS or conn.vendor != "postgresql":
        return
    with conn.cursor() as cursor:
        if schema:
            cursor.execute(f"SET search_path = {schema}, public")
        else:
            cursor.execute("SET search_path TO DEFAULT")


@contextlib.contextmanager
def activated_site(site):
    token = active_schema.set(site.schema_name)
    try:
        set_search_path(site.schema_name)
        yield site
    finally:
        set_search_path(None)
        active_schema.reset(token)


class VaranusSchemaRouter:
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "varanus" and db != settings.VARANUS_DB_ALIAS:
            # Don't migrate varanus models to any database except VARANUS_DB_ALIAS.
            return False
        if (
            not settings.VARANUS_USE_SCHEMAS
            or connections[settings.VARANUS_DB_ALIAS].vendor != "postgresql"
        ):
            # If we're not using schemas, fall back to default behavior.
            return None

        is_schema_model = app_label == "varanus" and model_name in (
            # "node",
            # "nodeupdate",
            # "nodepackage",
            "request",
            "context",
            "error",
            "log",
            "metric",
            "query",
            "contextintegration",
        )
        try:
            # If there is an activated schema, only migrate the schema models.
            active_schema.get()
            return is_schema_model
        except LookupError:
            # Otherwise, only migrate the non-schema models.
            if is_schema_model:
                return False

    def db_for_read(self, model, **hints):
        if model._meta.app_label == "varanus":
            return settings.VARANUS_DB_ALIAS

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "varanus":
            return settings.VARANUS_DB_ALIAS
