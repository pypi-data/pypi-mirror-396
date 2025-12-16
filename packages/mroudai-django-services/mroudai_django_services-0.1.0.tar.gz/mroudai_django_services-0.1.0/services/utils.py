from __future__ import annotations

from typing import Iterable, Optional, Type

from django.db import models
from django.utils.text import slugify


def generate_unique_slug(
    instance: models.Model,
    value: str,
    slug_field_name: str = "slug",
    extra_filter: Optional[models.Q] = None,
) -> str:
    """
    Generate a slug, suffixing with -2, -3, etc. to avoid collisions.
    If extra_filter is provided it is applied to the queryset when checking collisions.
    """
    base_slug = slugify(value) or "item"
    slug = base_slug
    Model: Type[models.Model] = instance.__class__
    queryset = Model._default_manager.all()
    if extra_filter is not None:
        queryset = queryset.filter(extra_filter)

    def slug_exists(candidate: str) -> bool:
        lookup = {slug_field_name: candidate}
        return queryset.filter(**lookup).exclude(pk=getattr(instance, "pk", None)).exists()

    counter = 2
    while slug_exists(slug):
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug
