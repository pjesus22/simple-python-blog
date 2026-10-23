import os

from .base import *

# CORE SETTINGS
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-test-only")
DEBUG = False
POST_RETENTION_DAYS = 30
API_PAGE_SIZE = 20

# SECURITY OPTIMIZATIONS (FOR SPEED)
AUTH_PASSWORD_VALIDATORS = []
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# LOGGING
LOGGING["root"]["level"] = "WARNING"
LOGGING["loggers"]["django"]["level"] = "WARNING"
LOGGING["loggers"]["django.request"]["level"] = "CRITICAL"
