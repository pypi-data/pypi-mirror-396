SECRET_KEY = "test-secret-key"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "tenants",
]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

MIDDLEWARE = []

ROOT_URLCONF = "tenants.tests.urls"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
