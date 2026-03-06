import os

from .base import *

DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"
SITE_DOMAIN = os.getenv("SITE_DOMAIN", "localhost:8000")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if os.getenv("CSRF_TRUSTED_ORIGINS") else []

# Email configuration
if os.getenv("EMAIL_HOST"):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
    EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "false").lower() == "true"
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@attendee.dev")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "attendee_development",
        "USER": "attendee_development_user",
        "PASSWORD": "attendee_development_user",
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": "5432",
    }
}

# Log more stuff in development
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "xmlschema": {"level": "WARNING", "handlers": ["console"], "propagate": False},
        # Uncomment to log database queries
        # "django.db.backends": {
        #    "handlers": ["console"],
        #    "level": "DEBUG",
        #    "propagate": False,
        # },
    },
}
