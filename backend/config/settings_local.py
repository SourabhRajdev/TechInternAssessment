"""
Local development settings using SQLite instead of PostgreSQL.
This allows running without Docker for testing.
"""
from .settings import *

# Override database to use SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Use local environment
DEBUG = True
ALLOWED_HOSTS = ['*']

# CORS for local development
CORS_ALLOW_ALL_ORIGINS = True

print("🔧 Using SQLite database for local development")
