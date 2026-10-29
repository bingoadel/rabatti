import os
from pathlib import Path

# BASE_DIR zeigt auf den Projektordner. Django verwendet dies als Basis für
# Templates, statische Dateien und andere Pfade.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-dev-key-change-me"

DEBUG = True

ALLOWED_HOSTS = ['rabattparty.de', 'www.rabattparty.de', '87.106.41.173', '127.0.0.1', 'localhost']

# Hinzufügen, damit Django HTTPS-Formulare von Ihrer Domain akzeptiert:
CSRF_TRUSTED_ORIGINS = [
    'https://rabattparty.de',
    'https://www.rabattparty.de'
]


# INSTALLED_APPS listet alle Django-Apps auf, die geladen werden sollen.
# "models" ist die App für die Datenbankschicht. Views und Templates liegen
# daneben in den Ordnern views/ und templates/.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "models",
]

# same-origin würde die Herkunft der Seite vor den Kartenkacheln verbergen.
# Der Kartendienst lehnt solche Abrufe mit 403 ab.
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Produktarten und ihre Zusammensetzung. Nur aktiv, wenn Postgres erreichbar
# sein soll. Ohne POSTGRES_HOST bleibt die übrige Anwendung bei SQLite.
_postgres_host = os.environ.get("POSTGRES_HOST", "").strip()
if _postgres_host:
    DATABASES["composition"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "rabatti"),
        "USER": os.environ.get("POSTGRES_USER", "rabatti"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "rabatti"),
        "HOST": _postgres_host,
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }

DATABASE_ROUTERS = ["models.composition_router.CompositionRouter"]

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

LANGUAGE_CODE = "de-de"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
# Zielordner für collectstatic. Getrennt von static/, sonst bricht der Image-Bau ab.
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
