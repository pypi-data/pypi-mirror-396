"""Django settings for SafePass"""

import os
from pathlib import Path
import secrets

# Build paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path.home() / ".safepass"
DATA_DIR.mkdir(exist_ok=True)

# Secret key
SECRET_KEY_FILE = DATA_DIR / "secret.key"
if SECRET_KEY_FILE.exists():
    SECRET_KEY = SECRET_KEY_FILE.read_text().strip()
else:
    SECRET_KEY = secrets.token_urlsafe(50)
    SECRET_KEY_FILE.write_text(SECRET_KEY)

# Debug mode (set SAFEPASS_DEBUG=0 in environment to disable)
DEBUG = os.environ.get('SAFEPASS_DEBUG', '1') == '1'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Application definition
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'corsheaders',
    'safepass',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'safepass.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
            ],
        },
    },
]

WSGI_APPLICATION = 'safepass.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATA_DIR / 'db.sqlite3',
    }
}

# Cache configuration for sessions
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'safepass-session-cache',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
]

# Internationalization
LANGUAGE_CODE = 'tr-tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# CSRF settings
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

# Session settings
# Use cache backend so sessions are cleared on server restart
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
SESSION_TIMEOUT = 3600  # 1 hour inactivity timeout (in seconds)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Session expires when browser closes
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'safepass.User'
