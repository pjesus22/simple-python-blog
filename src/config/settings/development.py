import os

from .base import *

# CORE SETTINGS
SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = True
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
    if host.strip()
]

# LOGGING
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
LOGGING["root"]["level"] = LOG_LEVEL
LOGGING["loggers"]["django"]["level"] = LOG_LEVEL
