from __future__ import annotations

from typing import Iterable, Optional

from django.conf import settings


def get_setting(name: str, default):
    return getattr(settings, name, default)


def tenant_model() -> Optional[str]:
    return get_setting("SERVICES_TENANT_MODEL", None)


def default_currency() -> str:
    return get_setting("SERVICES_DEFAULT_CURRENCY", "TTD")


def allowed_intervals() -> Iterable[int]:
    return get_setting("SERVICES_ALLOWED_INTERVALS", [5, 10, 12, 15, 20, 30, 60])


def min_duration_minutes() -> int:
    return get_setting("SERVICES_MIN_DURATION_MINUTES", 5)
