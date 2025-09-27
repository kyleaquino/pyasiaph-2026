import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from config.environment import settings, BASE_DIR

SECRET_KEY = settings.SECRET_KEY

DEBUG = settings.DEBUG

ALLOWED_HOSTS = settings.get_allowed_hosts()

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

WHITENOISE_COMPRESS = True

WHITENOISE_MAX_AGE = 31536000

CSRF_TRUSTED_ORIGINS = settings.get_trusted_origins()

SECURE_REFERRER_POLICY = "no-referrer-when-downgrade"

SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"

CORS_ALLOWED_ORIGINS = settings.get_trusted_origins()

if settings.APP_ENV == "development":
    CORS_ALLOW_ALL_ORIGINS = True

THIRD_PARTY_APPS = [
    "compressor",
    "django_extensions",
    "django_browser_reload",
    "django_watchfiles",
]

LOCAL_APPS = [
    "pyasiaph.content",
    "pyasiaph.home",
    "pyasiaph.search",
    "pyasiaph.presentations",
    "pyasiaph.sponsors",
]

WAGTAIL_APPS = [
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.search_promotions",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
]

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

INSTALLED_APPS = [
    *WAGTAIL_APPS,
    *DJANGO_APPS,
    *THIRD_PARTY_APPS,
    *LOCAL_APPS,
]

LOCAL_MIDDLEWARE = [
    "config.middleware.HealthCheckMiddleware",
]

THIRD_PARTY_MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

DJANGO_MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
]

WAGTAIL_MIDDLEWARE = [
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

MIDDLEWARE = [
    *LOCAL_MIDDLEWARE,
    *THIRD_PARTY_MIDDLEWARE,
    *DJANGO_MIDDLEWARE,
    *WAGTAIL_MIDDLEWARE,
]

if settings.APP_ENV == "development":
    INSTALLED_APPS.insert(0, "whitenoise.runserver_nostatic")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "config/templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

if settings.APP_ENV == "development":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "DISABLE_SERVER_SIDE_CURSORS": True,
            **settings.db_config(),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_DIRS = [
    BASE_DIR / "config/static",
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"

MEDIA_ROOT = BASE_DIR / "mediafiles"
MEDIA_URL = "/media/"


# Compressor
# https://django-compressor.readthedocs.io/en/stable/index.html

COMPRESS_ROOT = STATIC_ROOT

COMPRESS_URL = STATIC_URL

COMPRESS_ENABLED = True

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)


# Wagtail settings

WAGTAIL_SITE_NAME = settings.SITE_NAME

WAGTAILSEARCH_BACKENDS = {"default": {"BACKEND": "wagtail.search.backends.database"}}

WAGTAIL_WORKFLOW_ENABLED = False

WAGTAILADMIN_BASE_URL = settings.BASE_URL


# Sentry settings
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "django_watchfiles": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "watchfiles": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
