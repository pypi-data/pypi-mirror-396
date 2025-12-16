from __future__ import annotations

from decimal import Decimal
from typing import Optional

from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from . import conf
from .utils import generate_unique_slug

TENANT_MODEL = conf.tenant_model()
HAS_TENANCY = bool(TENANT_MODEL)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ServiceCategory(TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=False, blank=True)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    if HAS_TENANCY:
        tenant = models.ForeignKey(
            TENANT_MODEL,
            on_delete=models.CASCADE,
            related_name="service_categories",
        )

    class Meta:
        ordering = ["sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["slug"] if not HAS_TENANCY else ["tenant", "slug"],
                name="services_category_slug_unique"
                if not HAS_TENANCY
                else "services_category_slug_tenant_unique",
            )
        ]
        indexes = []
        if HAS_TENANCY:
            indexes.append(models.Index(fields=["tenant", "is_active", "sort_order"]))
        else:
            indexes.append(models.Index(fields=["is_active", "sort_order"]))

    def clean(self):
        super().clean()
        if HAS_TENANCY and not getattr(self, "tenant", None):
            raise ValidationError({"tenant": _("Tenant is required.")})

    def save(self, *args, **kwargs):
        if not self.slug:
            extra_filter = Q()
            if HAS_TENANCY and getattr(self, "tenant_id", None):
                extra_filter = Q(tenant_id=self.tenant_id)
            self.slug = generate_unique_slug(self, self.name, extra_filter=extra_filter)
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Service(TimeStampedModel):
    class Visibility(models.TextChoices):
        PUBLIC = "public", _("Public")
        PRIVATE = "private", _("Private")

    class PricingType(models.TextChoices):
        FREE = "free", _("Free")
        FIXED = "fixed", _("Fixed")
        FROM = "from", _("From")
        VARIABLE = "variable", _("Variable")

    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="services",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    visibility = models.CharField(
        max_length=10, choices=Visibility.choices, default=Visibility.PUBLIC
    )
    sort_order = models.IntegerField(default=0)

    duration_minutes = models.PositiveIntegerField()
    buffer_before_minutes = models.PositiveIntegerField(default=0)
    buffer_after_minutes = models.PositiveIntegerField(default=0)
    minimum_notice_minutes = models.PositiveIntegerField(default=0)
    maximum_advance_days = models.PositiveIntegerField(default=365)
    fixed_start_times_only = models.BooleanField(default=False)
    start_time_interval_minutes = models.PositiveIntegerField(default=15)

    capacity = models.PositiveIntegerField(default=1)
    allow_multiple_clients_per_slot = models.BooleanField(default=False)

    pricing_type = models.CharField(
        max_length=10, choices=PricingType.choices, default=PricingType.FIXED
    )
    price_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    currency = models.CharField(max_length=3, default=conf.default_currency)

    requires_approval = models.BooleanField(default=False)
    cancellation_allowed = models.BooleanField(default=True)
    cancellation_notice_minutes = models.PositiveIntegerField(default=0)
    reschedule_allowed = models.BooleanField(default=True)
    reschedule_notice_minutes = models.PositiveIntegerField(default=0)

    metadata = models.JSONField(default=dict, blank=True)

    if HAS_TENANCY:
        tenant = models.ForeignKey(
            TENANT_MODEL,
            on_delete=models.CASCADE,
            related_name="services",
        )

    class Meta:
        ordering = ["sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["slug"] if not HAS_TENANCY else ["tenant", "slug"],
                name="services_service_slug_unique"
                if not HAS_TENANCY
                else "services_service_slug_tenant_unique",
            ),
            models.CheckConstraint(
                condition=Q(maximum_advance_days__gte=1),
                name="services_service_max_advance_positive",
            ),
        ]
        indexes = []
        if HAS_TENANCY:
            indexes.extend(
                [
                    models.Index(fields=["tenant", "is_active", "sort_order"]),
                    models.Index(fields=["tenant", "category", "is_active"]),
                    models.Index(fields=["tenant", "visibility", "is_active"]),
                ]
            )
        else:
            indexes.extend(
                [
                    models.Index(fields=["is_active", "sort_order"]),
                    models.Index(fields=["category", "is_active"]),
                    models.Index(fields=["visibility", "is_active"]),
                ]
            )

    def clean(self):
        super().clean()

        if HAS_TENANCY and not getattr(self, "tenant", None):
            raise ValidationError({"tenant": _("Tenant is required.")})

        min_duration = conf.min_duration_minutes()
        if self.duration_minutes < min_duration:
            raise ValidationError(
                {"duration_minutes": _(f"Duration must be at least {min_duration} minutes.")}
            )

        allowed_intervals = list(conf.allowed_intervals())
        if self.fixed_start_times_only and self.start_time_interval_minutes not in allowed_intervals:
            raise ValidationError(
                {
                    "start_time_interval_minutes": _(
                        f"Start interval must be one of: {', '.join(map(str, allowed_intervals))}."
                    )
                }
            )

        pricing_errors = self._validate_pricing()
        if pricing_errors:
            raise ValidationError(pricing_errors)

        if not self.allow_multiple_clients_per_slot and self.capacity > 1:
            raise ValidationError(
                {
                    "capacity": _(
                        "Capacity must be 1 when multiple clients per slot are not allowed."
                    )
                }
            )

    def _validate_pricing(self):
        errors = {}
        if self.pricing_type == self.PricingType.FREE:
            if self.price_amount not in (None, Decimal("0")):
                errors["price_amount"] = _("Free services must not have a price.")
            self.price_amount = None
        elif self.pricing_type in (self.PricingType.FIXED, self.PricingType.FROM):
            if self.price_amount is None:
                errors["price_amount"] = _("Price is required for fixed/from pricing.")
            elif self.price_amount < 0:
                errors["price_amount"] = _("Price must be zero or positive.")
        elif self.pricing_type == self.PricingType.VARIABLE:
            if self.price_amount is not None:
                errors["price_amount"] = _("Variable pricing must not set price_amount.")
            self.price_amount = None
        return errors

    def save(self, *args, **kwargs):
        if not self.slug:
            extra_filter = Q()
            if HAS_TENANCY and getattr(self, "tenant_id", None):
                extra_filter = Q(tenant_id=self.tenant_id)
            self.slug = generate_unique_slug(self, self.name, extra_filter=extra_filter)
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ServiceAddon(TimeStampedModel):
    class PricingType(models.TextChoices):
        FREE = "free", _("Free")
        FIXED = "fixed", _("Fixed")
        FROM = "from", _("From")
        VARIABLE = "variable", _("Variable")

    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="addons"
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    extra_duration_minutes = models.PositiveIntegerField(default=0)
    pricing_type = models.CharField(
        max_length=10, choices=PricingType.choices, default=PricingType.FIXED
    )
    price_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    currency = models.CharField(max_length=3, blank=True)

    if HAS_TENANCY:
        tenant = models.ForeignKey(
            TENANT_MODEL,
            on_delete=models.CASCADE,
            related_name="service_addons",
        )

    class Meta:
        ordering = ["sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["service", "slug"],
                name="services_addon_slug_service_unique",
            )
        ]

    def clean(self):
        super().clean()
        errors = {}

        if HAS_TENANCY:
            if not getattr(self, "tenant", None):
                errors["tenant"] = _("Tenant is required.")
            elif getattr(self.service, "tenant_id", None) != getattr(self, "tenant_id", None):
                errors["tenant"] = _("Addon tenant must match the service tenant.")

        if not self.currency and self.service_id:
            self.currency = self.service.currency

        pricing_errors = self._validate_pricing()
        errors.update(pricing_errors)

        if errors:
            raise ValidationError(errors)

    def _validate_pricing(self):
        errors = {}
        if self.pricing_type == self.PricingType.FREE:
            if self.price_amount not in (None, Decimal("0")):
                errors["price_amount"] = _("Free add-ons must not have a price.")
            self.price_amount = None
        elif self.pricing_type in (self.PricingType.FIXED, self.PricingType.FROM):
            if self.price_amount is None:
                errors["price_amount"] = _("Price is required for fixed/from pricing.")
            elif self.price_amount < 0:
                errors["price_amount"] = _("Price must be zero or positive.")
        elif self.pricing_type == self.PricingType.VARIABLE:
            if self.price_amount is not None:
                errors["price_amount"] = _("Variable pricing must not set price_amount.")
            self.price_amount = None
        return errors

    def save(self, *args, **kwargs):
        if not self.currency:
            self.currency = self.service.currency
        if not self.slug:
            self.slug = generate_unique_slug(
                self, self.name, extra_filter=Q(service_id=self.service_id)
            )
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.service})"
