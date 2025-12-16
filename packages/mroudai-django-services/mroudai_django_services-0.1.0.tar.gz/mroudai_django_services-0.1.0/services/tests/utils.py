import importlib

from django.apps import apps


def reload_services_models():
    """
    Reload services models so tenancy setting changes are respected.
    """
    if "services" in apps.all_models:
        apps.all_models.pop("services", None)
    apps.clear_cache()
    importlib.invalidate_caches()
    import services.models as services_models  # noqa: F401
    importlib.reload(services_models)
    import services  # noqa: F401
    importlib.reload(services)
    return services_models
