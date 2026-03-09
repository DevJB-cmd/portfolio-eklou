"""
Django settings for portfolio project.
"""

import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "change-me-in-production-with-a-long-random-secret",
)

DEBUG = env_bool("DJANGO_DEBUG", default=False)
RUNNING_TESTS = "test" in sys.argv

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,*")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "monportfolio",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "monportfolio.middleware.RateLimitMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "monportfolio.middleware.ActivityLogMiddleware",
    "monportfolio.middleware.SecurityHeadersMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "portfolio.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "monportfolio.context_processors.branding",
            ],
        },
    },
]
WSGI_APPLICATION = "portfolio.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]


LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "Africa/Lome"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "portfolio-security-cache",
    }
}

SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", default=not DEBUG and not RUNNING_TESTS)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = int(os.getenv("DJANGO_SESSION_COOKIE_AGE", "3600"))
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

SECURE_HSTS_SECONDS = int(
    os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000" if not DEBUG else "0")
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

DATA_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

RATE_LIMITS = {
    "contact_post": {
        "path": "/contact/",
        "methods": {"POST"},
        "limit": 5,
        "window_seconds": 600,
    },
    "admin_login_ip": {
        "path": "/bitch/login/",
        "methods": {"POST"},
        "limit": 10,
        "window_seconds": 900,
    },
    "admin_login_legacy": {
        "path": "/admin/login/",
        "methods": {"POST"},
        "limit": 10,
        "window_seconds": 900,
    },
    "api_general": {
        "path_prefix": "/api/",
        "methods": {"GET", "POST", "PUT", "PATCH", "DELETE"},
        "limit": 100,
        "window_seconds": 60,
    },
    "activity_time_spent": {
        "path": "/activity/time-spent/",
        "methods": {"POST"},
        "limit": 120,
        "window_seconds": 60,
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": str(LOG_DIR / "system.log"),
            "formatter": "standard",
        },
    },
    "loggers": {
        "django.security": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
        "monportfolio.security": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "monportfolio.activity": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
