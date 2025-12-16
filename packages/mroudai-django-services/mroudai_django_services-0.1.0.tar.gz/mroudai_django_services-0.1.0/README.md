# django-services — Bookable services for Django projects

A reusable Django app (app label: `services`) that models bookable services, categories, and add-ons for appointment and booking platforms.

## What it provides
- Service categories, services, and service add-ons with pricing, durations, and buffers.
- Booking-time constraints: minimum notice, maximum advance window, and fixed start intervals.
- Admin experience with inlines for add-ons and sensible list filters.
- Optional tenant scoping via a configurable tenant model.

## What it does not provide
- Provider availability, slot generation, or calendars.
- Booking lifecycle or payments handling.
- Opinionated multi-tenant framework; only a light integration point.

## Installation
```bash
pip install mroudai-django-services
```
Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ...
    "services",
]
```

## Quick start (single-tenant)
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Create categories and services via the Django admin. Slugs are auto-generated and validated for collisions.

## Usage
Create categories/services programmatically:
```python
from services.models import ServiceCategory, Service

category = ServiceCategory.objects.create(name="Consultations")
service = Service.objects.create(
    name="Initial Consult",
    category=category,
    duration_minutes=30,
    pricing_type=Service.PricingType.FIXED,
    price_amount=200,
    minimum_notice_minutes=120,
    maximum_advance_days=30,
    fixed_start_times_only=True,
    start_time_interval_minutes=15,
)

# List active services
from services.selectors import list_services
active_services = list_services()
```
Add-ons with tenant matching (when enabled) are created via `ServiceAddon.objects.create(...)` and inherit currency if left blank.

## Multi-tenant configuration
Set `SERVICES_TENANT_MODEL` to your tenant model label (e.g. `"tenants.Tenant"`):
```python
SERVICES_TENANT_MODEL = "tenants.Tenant"
SERVICES_DEFAULT_CURRENCY = "TTD"
SERVICES_ALLOWED_INTERVALS = [5, 10, 12, 15, 20, 30, 60]
SERVICES_MIN_DURATION_MINUTES = 5
```
When `SERVICES_TENANT_MODEL` is set, categories, services, and add-ons include a required `tenant` foreign key and uniqueness constraints are scoped per tenant. Without it, data is global.

## Models overview
- **ServiceCategory**: name, slug, optional description, sort order, active flag; unique slug (per tenant when enabled).
- **Service**: category, name, slug, short/long description, duration, buffers, minimum notice, maximum advance, fixed start intervals, capacity and multi-client flag, pricing (`FREE`, `FIXED`, `FROM`, `VARIABLE`), currency, cancellation/reschedule rules, metadata.
- **ServiceAddon**: service, name, slug, description, active flag, sort order, extra duration, pricing (`FREE`, `FIXED`, `FROM`, `VARIABLE`), currency (defaults to service), tenant match enforced when enabled.

## Admin features
- Inline add-ons within a service.
- Filters for activity, visibility, pricing, category (and tenant when configured).
- Slug auto-generation with collision handling.
- Model validation enforced on save.

## Testing
```bash
python -m test services
```
For tenant-aware runs, override `SERVICES_TENANT_MODEL` to point at your tenant model and rerun the tests.

## Contributing
Issues and pull requests are welcome. Please keep changes small, add tests, and favour clear boundaries between apps. Early-stage API changes may occur as the package matures.

## Licence
MIT License.
