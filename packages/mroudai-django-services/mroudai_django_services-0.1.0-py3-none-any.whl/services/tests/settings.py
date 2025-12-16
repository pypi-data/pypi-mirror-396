SECRET_KEY = "test-secret"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "services",
    "services.tests.tenants",
]
DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
}
USE_TZ = True
MIGRATION_MODULES = {"services": None}
