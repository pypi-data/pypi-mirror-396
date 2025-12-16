from django.apps import AppConfig


class TenantsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.tests.tenants"
    label = "tests_tenants"
    verbose_name = "Test Tenants"
