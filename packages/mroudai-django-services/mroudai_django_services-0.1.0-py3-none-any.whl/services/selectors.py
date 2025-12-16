from __future__ import annotations

from typing import Optional

from django.db.models import QuerySet

from . import conf
from .models import Service, ServiceAddon


def _tenant_filter_kwargs(tenant=None) -> dict:
    if conf.tenant_model():
        return {"tenant": tenant} if tenant is not None else {}
    return {}


def list_services(
    *,
    tenant=None,
    include_inactive: bool = False,
    visibility: Optional[str] = None,
    category=None,
) -> QuerySet:
    qs = Service.objects.all()
    qs = qs.filter(**_tenant_filter_kwargs(tenant))
    if not include_inactive:
        qs = qs.filter(is_active=True)
    if visibility:
        qs = qs.filter(visibility=visibility)
    if category:
        qs = qs.filter(category=category)
    return qs


def get_service(*, slug: str, tenant=None, include_inactive: bool = False) -> Service:
    qs = list_services(tenant=tenant, include_inactive=include_inactive)
    return qs.get(slug=slug)


def list_addons(*, service: Service, include_inactive: bool = False) -> QuerySet:
    qs = ServiceAddon.objects.filter(service=service)
    qs = qs.filter(**_tenant_filter_kwargs(getattr(service, "tenant", None)))
    if not include_inactive:
        qs = qs.filter(is_active=True)
    return qs
