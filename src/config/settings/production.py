import os

from config.logging import JsonFormatter

from .base import *

# CORE SETTINGS
SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = False
ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(",")

# LOGGING
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

if LOG_LEVEL not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
    raise ValueError(f"Invalid LOG_LEVEL: {LOG_LEVEL}")

LOGGING["formatters"]["json"] = {"()": JsonFormatter}
LOGGING["handlers"]["console"]["formatter"] = "json"
LOGGING["root"]["level"] = LOG_LEVEL
LOGGING["loggers"]["django"]["level"] = LOG_LEVEL
