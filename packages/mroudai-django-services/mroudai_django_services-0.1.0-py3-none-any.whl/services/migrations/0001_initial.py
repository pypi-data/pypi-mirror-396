from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import services.conf


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ServiceCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(blank=True, max_length=255)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["sort_order", "name"],
            },
        ),
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(blank=True, max_length=255)),
                ("short_description", models.CharField(blank=True, max_length=255)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("visibility", models.CharField(choices=[("public", "Public"), ("private", "Private")], default="public", max_length=10)),
                ("sort_order", models.IntegerField(default=0)),
                ("duration_minutes", models.PositiveIntegerField()),
                ("buffer_before_minutes", models.PositiveIntegerField(default=0)),
                ("buffer_after_minutes", models.PositiveIntegerField(default=0)),
                ("minimum_notice_minutes", models.PositiveIntegerField(default=0)),
                ("maximum_advance_days", models.PositiveIntegerField(default=365)),
                ("fixed_start_times_only", models.BooleanField(default=False)),
                ("start_time_interval_minutes", models.PositiveIntegerField(default=15)),
                ("capacity", models.PositiveIntegerField(default=1)),
                ("allow_multiple_clients_per_slot", models.BooleanField(default=False)),
                ("pricing_type", models.CharField(choices=[("free", "Free"), ("fixed", "Fixed"), ("from", "From"), ("variable", "Variable")], default="fixed", max_length=10)),
                ("price_amount", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("currency", models.CharField(default=services.conf.default_currency, max_length=3)),
                ("requires_approval", models.BooleanField(default=False)),
                ("cancellation_allowed", models.BooleanField(default=True)),
                ("cancellation_notice_minutes", models.PositiveIntegerField(default=0)),
                ("reschedule_allowed", models.BooleanField(default=True)),
                ("reschedule_notice_minutes", models.PositiveIntegerField(default=0)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="services", to="services.servicecategory")),
            ],
            options={
                "ordering": ["sort_order", "name"],
            },
        ),
        migrations.CreateModel(
            name="ServiceAddon",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(blank=True, max_length=255)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.IntegerField(default=0)),
                ("extra_duration_minutes", models.PositiveIntegerField(default=0)),
                ("pricing_type", models.CharField(choices=[("free", "Free"), ("fixed", "Fixed"), ("from", "From"), ("variable", "Variable")], default="fixed", max_length=10)),
                ("price_amount", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("currency", models.CharField(blank=True, max_length=3)),
                ("service", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="addons", to="services.service")),
            ],
            options={
                "ordering": ["sort_order", "name"],
            },
        ),
        migrations.AddConstraint(
            model_name="servicecategory",
            constraint=models.UniqueConstraint(fields=("slug",), name="services_category_slug_unique"),
        ),
        migrations.AddIndex(
            model_name="servicecategory",
            index=models.Index(fields=["is_active", "sort_order"], name="services_se_is_act_e50707_idx"),
        ),
        migrations.AddConstraint(
            model_name="service",
            constraint=models.UniqueConstraint(fields=("slug",), name="services_service_slug_unique"),
        ),
        migrations.AddConstraint(
            model_name="service",
            constraint=models.CheckConstraint(condition=models.Q(("maximum_advance_days__gte", 1)), name="services_service_max_advance_positive"),
        ),
        migrations.AddIndex(
            model_name="service",
            index=models.Index(fields=["is_active", "sort_order"], name="services_se_is_act_19b8c4_idx"),
        ),
        migrations.AddIndex(
            model_name="service",
            index=models.Index(fields=["category", "is_active"], name="services_se_categor_ba4a62_idx"),
        ),
        migrations.AddIndex(
            model_name="service",
            index=models.Index(fields=["visibility", "is_active"], name="services_se_visibil_58b700_idx"),
        ),
        migrations.AddConstraint(
            model_name="serviceaddon",
            constraint=models.UniqueConstraint(fields=("service", "slug"), name="services_addon_slug_service_unique"),
        ),
    ]
