import os

from .base import *

# CORE SETTINGS
SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = True
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]
POST_RETENTION_DAYS = int(os.getenv("POST_RETENTION_DAYS", "30"))

# APPS
INSTALLED_APPS += [
    "django_extensions",
]

# DATABASE CONFIGURATION
DATABASES["default"]["NAME"] = Path(
    os.getenv("DATABASE_PATH", str(BASE_DIR / "db.sqlite3"))
)

# LOGGING
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
LOGGING["root"]["level"] = LOG_LEVEL
LOGGING["loggers"]["django"]["level"] = LOG_LEVEL
