import os
import secrets
from pathlib import Path

import passkeys
from cconf import (
    CommaSeparatedStrings,
    DatabaseDict,
    Duration,
    EnvFile,
    HostEnv,
    Recipients,
    Secret,
    config,
)

if base_dir := os.getenv("BASE_DIR"):
    BASE_DIR = Path(base_dir)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

config.setup(
    HostEnv(),
    EnvFile(BASE_DIR / ".env"),
)

DATA_DIR = config("DATA_DIR", BASE_DIR / "data", cast=Path)
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

SECRET_KEY = config("SECRET_KEY", None, cast=Secret)
if not SECRET_KEY:
    secret_path = os.path.join(DATA_DIR, "secret.key")
    if os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            SECRET_KEY = f.read().strip()
    else:
        with open(os.path.join(DATA_DIR, "secret.key"), "w") as f:
            SECRET_KEY = secrets.token_urlsafe(50)
            f.write(SECRET_KEY)

DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=CommaSeparatedStrings)
ADMINS = config("ADMINS", "", cast=Recipients)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "varanus.server.apps.VaranusServer",
    "varanus.search",
    "varanus.tasks",
    "cconf",
    "passkeys",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "varanus.server.urls"

template_loaders = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]
if not DEBUG:
    template_loaders = [("django.template.loaders.cached.Loader", template_loaders)]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [passkeys.template_directory],
        "OPTIONS": {
            "loaders": template_loaders,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "varanus.server.context_processors.sites",
            ],
        },
    },
]

WSGI_APPLICATION = "varanus.server.wsgi.application"

# https://forum.djangoproject.com/t/sqlite-and-database-is-locked-error/26994
DATABASES = {
    "default": config(
        "DATABASE_URL",
        f"sqlite:///{DATA_DIR}/db.sqlite3?transaction_mode=IMMEDIATE",
        cast=DatabaseDict(ATOMIC_REQUESTS=True, TEST={"MIGRATE": False}),
    ),
}

DATABASE_ROUTERS = [
    "varanus.server.router.VaranusSchemaRouter",
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

TASKS = {
    "default": {
        "BACKEND": "varanus.tasks.backend.DatabaseBackend",
        "OPTIONS": {
            "immediate": False,
            "retain": Duration("1w"),
        },
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "basic": {
            "format": "{asctime} [{levelname} - {name}:{lineno}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "basic",
        },
        "varanus": {
            "class": "varanus.client.loggers.VaranusHandler",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "varanus": {
            "handlers": ["console", "varanus"],
            "level": "DEBUG",
        },
    },
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = config("TIME_ZONE", default="America/New_York")
USE_I18N = True
USE_TZ = True

STATIC_ROOT = config("STATIC_ROOT", default=BASE_DIR / "static", cast=Path)
STATIC_URL = config("STATIC_URL", "static/")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"

# Sessions

SESSION_COOKIE_DOMAIN = config("SESSION_COOKIE_DOMAIN", None)
SESSION_COOKIE_NAME = config("SESSION_COOKIE_NAME", "varanus_session")
SESSION_COOKIE_AGE = int(
    config("SESSION_COOKIE_AGE", "365d", cast=Duration).total_seconds()
)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", False, cast=bool)

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", [], cast=CommaSeparatedStrings)

# Email

_default_mod = "console" if DEBUG else "smtp"
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", f"django.core.mail.backends.{_default_mod}.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", "localhost")
EMAIL_PORT = config("EMAIL_PORT", 25, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", "root@localhost")

# Varanus

VARANUS_DB_ALIAS = config("VARANUS_DB_ALIAS", default="default")
VARANUS_USE_SCHEMAS = config("VARANUS_USE_SCHEMAS", default=False, cast=bool)
VARANUS_INTERNAL = config("VARANUS_INTERNAL", default=False, cast=bool)

if VARANUS_INTERNAL:
    import varanus.client

    varanus.client.setup(
        "db://__internal__",
        environment="internal",
        include_headers=True,
        include_settings=True,
        include_env=True,
        # log_queries=True,
        # log_query_params=True,
        # log_query_stack=True,
        query_metrics=True,
        install=MIDDLEWARE,
    )
