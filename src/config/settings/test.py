import os

from .base import *

# CORE SETTINGS
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-test-only")
DEBUG = False

# LOGGING
LOGGING["root"]["level"] = "WARNING"
LOGGING["loggers"]["django"]["level"] = "WARNING"
LOGGING["loggers"]["django.request"]["level"] = "CRITICAL"
