"""
Django settings for config project with SQLite database for testing.
"""

from .settings import *

# Override database to use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_test.sqlite3',
    }
}

# Ensure we can run admin interface
INSTALLED_APPS = [
    'django.contrib.admin',  # Add admin
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    # Local apps
    'api',
    'frontend',
]

# Enable admin URLs
ROOT_URLCONF = 'config.urls'