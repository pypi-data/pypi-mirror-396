from datetime import timedelta
import importlib

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase, TransactionTestCase, override_settings
from django.utils import timezone

from services import conf
from services.validators import validate_service_time_constraints


class SlugGenerationTests(TestCase):
    def test_category_slug_collision(self):
        from services.models import ServiceCategory

        cat1 = ServiceCategory.objects.create(name="Haircut")
        cat2 = ServiceCategory.objects.create(name="Haircut")
        self.assertEqual(cat1.slug, "haircut")
        self.assertEqual(cat2.slug, "haircut-2")

    def test_service_slug_collision(self):
        from services.models import Service

        s1 = Service.objects.create(
            name="Massage",
            duration_minutes=30,
            pricing_type=Service.PricingType.FREE,
        )
        s2 = Service.objects.create(
            name="Massage",
            duration_minutes=45,
            pricing_type=Service.PricingType.FREE,
        )
        self.assertEqual(s1.slug, "massage")
        self.assertEqual(s2.slug, "massage-2")


class PricingValidationTests(TestCase):
    def test_service_pricing_rules(self):
        from services.models import Service

        s = Service(name="Consult", duration_minutes=30, pricing_type=Service.PricingType.FREE)
        s.full_clean()
        s.save()
        self.assertIsNone(s.price_amount)

        s.pricing_type = Service.PricingType.FIXED
        s.price_amount = None
        with self.assertRaises(ValidationError):
            s.full_clean()

        s.price_amount = -1
        with self.assertRaises(ValidationError):
            s.full_clean()

        s.pricing_type = Service.PricingType.VARIABLE
        s.price_amount = 10
        with self.assertRaises(ValidationError):
            s.full_clean()

    def test_addon_pricing_rules(self):
        from services.models import Service, ServiceAddon

        service = Service.objects.create(
            name="Consult",
            duration_minutes=30,
            pricing_type=Service.PricingType.FREE,
        )
        addon = ServiceAddon(
            service=service,
            name="Report",
            pricing_type=ServiceAddon.PricingType.FREE,
        )
        addon.full_clean()
        addon.pricing_type = ServiceAddon.PricingType.FIXED
        addon.price_amount = None
        with self.assertRaises(ValidationError):
            addon.full_clean()
        addon.price_amount = 0
        addon.full_clean()


class CapacityTests(TestCase):
    def test_capacity_requires_flag(self):
        from services.models import Service

        service = Service(
            name="Workshop",
            duration_minutes=60,
            pricing_type=Service.PricingType.FREE,
            capacity=2,
            allow_multiple_clients_per_slot=False,
        )
        with self.assertRaises(ValidationError):
            service.full_clean()


class IntervalValidationTests(TestCase):
    def test_interval_validation(self):
        from services.models import Service

        service = Service.objects.create(
            name="Yoga",
            duration_minutes=60,
            pricing_type=Service.PricingType.FREE,
            fixed_start_times_only=True,
            start_time_interval_minutes=15,
        )
        now = timezone.now()
        start = (now + timedelta(hours=1)).replace(minute=7)
        errors = validate_service_time_constraints(service, start, now_dt=now)
        self.assertIn("Start time is not aligned to the required interval.", errors)

    def test_min_max_constraints(self):
        from services.models import Service

        now = timezone.now()
        service = Service.objects.create(
            name="Checkup",
            duration_minutes=30,
            pricing_type=Service.PricingType.FREE,
            minimum_notice_minutes=120,
            maximum_advance_days=1,
        )
        too_soon = now + timedelta(minutes=30)
        too_far = now + timedelta(days=5)
        errors_soon = validate_service_time_constraints(service, too_soon, now_dt=now)
        errors_far = validate_service_time_constraints(service, too_far, now_dt=now)
        self.assertIn("Booking does not meet the minimum notice period.", errors_soon)
        self.assertIn("Booking exceeds the maximum advance window.", errors_far)


@override_settings(SERVICES_TENANT_MODEL="tests_tenants.Tenant")
class TenancyTests(TransactionTestCase):
    reset_sequences = True

    @classmethod
    def setUpClass(cls):
        from services.tests.utils import reload_services_models
        from django.db import connection
        from django.conf import settings

        settings.SERVICES_TENANT_MODEL = "tests_tenants.Tenant"
        models = reload_services_models()
        assert hasattr(models.Service, "tenant"), "Tenant field was not added."
        # Recreate tables with tenant columns for this configuration.
        with connection.schema_editor() as editor:
            table_names = connection.introspection.table_names()
            for model in [models.ServiceAddon, models.Service, models.ServiceCategory]:
                if model._meta.db_table in table_names:
                    editor.delete_model(model)
            for model in [models.ServiceCategory, models.Service, models.ServiceAddon]:
                editor.create_model(model)
        super().setUpClass()

    def setUp(self):
        from services.tests.tenants.models import Tenant
        from services.tests.utils import reload_services_models

        models = reload_services_models()
        self.ServiceCategory = models.ServiceCategory
        self.Service = models.Service
        self.ServiceAddon = models.ServiceAddon
        self.tenant1 = Tenant.objects.create(name="Tenant 1")
        self.tenant2 = Tenant.objects.create(name="Tenant 2")

    def test_slug_collision_per_tenant(self):
        s1 = self.Service.objects.create(
            name="Massage",
            duration_minutes=30,
            tenant=self.tenant1,
            pricing_type=self.Service.PricingType.FREE,
        )
        s2 = self.Service.objects.create(
            name="Massage",
            duration_minutes=30,
            tenant=self.tenant2,
            pricing_type=self.Service.PricingType.FREE,
        )
        s3 = self.Service.objects.create(
            name="Massage",
            duration_minutes=45,
            tenant=self.tenant1,
            pricing_type=self.Service.PricingType.FREE,
        )
        self.assertEqual(s1.slug, "massage")
        self.assertEqual(s2.slug, "massage")
        self.assertEqual(s3.slug, "massage-2")

    def test_addon_tenant_consistency(self):
        service = self.Service.objects.create(
            name="Consult",
            duration_minutes=30,
            tenant=self.tenant1,
            pricing_type=self.Service.PricingType.FREE,
        )
        addon = self.ServiceAddon(
            service=service,
            name="Report",
            pricing_type=self.ServiceAddon.PricingType.FIXED,
            price_amount=10,
            tenant=self.tenant2,
        )
        with self.assertRaises(ValidationError):
            addon.full_clean()
