"""Development settings — SQLite, console email, relaxed security."""
from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Emails print to the terminal instead of sending — perfect for local testing.
# Set SEND_REAL_EMAILS=True in .env (with a valid Gmail app password) to make
# development send through SMTP for real.
if env_bool("SEND_REAL_EMAILS", False):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Plain static storage locally (no manifest hashing while developing).
STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}  # noqa

CORS_ALLOW_ALL_ORIGINS = True
