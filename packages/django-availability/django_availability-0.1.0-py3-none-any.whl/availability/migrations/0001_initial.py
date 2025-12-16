from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def build_models(has_tenant: bool, provider_model: str, tenant_model: str | None):
    indexes_weekly = [models.Index(fields=["provider", "weekday", "is_active"], name="avail_weekly_active_idx")]
    indexes_break = [models.Index(fields=["provider", "weekday", "is_active"], name="avail_break_active_idx")]
    indexes_exception = [models.Index(fields=["provider", "date"], name="avail_exc_provider_date_idx")]

    weekly_fields = [
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("weekday", models.IntegerField(choices=[(i, i) for i in range(7)])),
        ("start_time", models.TimeField()),
        ("end_time", models.TimeField()),
        ("is_active", models.BooleanField(default=True)),
        ("sort_order", models.IntegerField(default=0)),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        (
            "provider",
            models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="weekly_availability",
                to=provider_model,
            ),
        ),
    ]

    break_fields = [
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("weekday", models.IntegerField(choices=[(i, i) for i in range(7)])),
        ("start_time", models.TimeField()),
        ("end_time", models.TimeField()),
        ("is_active", models.BooleanField(default=True)),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        (
            "provider",
            models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="availability_breaks",
                to=provider_model,
            ),
        ),
    ]

    exception_fields = [
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("date", models.DateField()),
        ("kind", models.CharField(choices=[("closed", "Closed"), ("special_hours", "Special hours")], max_length=32)),
        ("start_time", models.TimeField(blank=True, null=True)),
        ("end_time", models.TimeField(blank=True, null=True)),
        ("note", models.CharField(blank=True, max_length=255)),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        (
            "provider",
            models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="availability_exceptions",
                to=provider_model,
            ),
        ),
    ]

    holidays_model = None
    operations = []

    if has_tenant:
        weekly_fields.append(
            (
                "tenant",
                models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="weekly_availability",
                    to=tenant_model,
                ),
            ),
        )
        indexes_weekly.append(
            models.Index(fields=["tenant", "provider", "weekday", "is_active"], name="avail_weekly_tenant_idx")
        )

        break_fields.append(
            (
                "tenant",
                models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="availability_breaks",
                    to=tenant_model,
                ),
            ),
        )
        indexes_break.append(
            models.Index(fields=["tenant", "provider", "weekday", "is_active"], name="avail_break_tenant_idx")
        )

        exception_fields.append(
            (
                "tenant",
                models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="availability_exceptions",
                    to=tenant_model,
                ),
            ),
        )
        indexes_exception.append(
            models.Index(fields=["tenant", "provider", "date"], name="avail_exc_tenant_date_idx")
        )

        holidays_model = migrations.CreateModel(
            name="TenantHoliday",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("name", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="availability_holidays",
                        to=tenant_model,
                    ),
                ),
            ],
            options={
                "ordering": ["date"],
                "unique_together": {("tenant", "date")},
                "indexes": [
                    models.Index(fields=["tenant", "date"], name="avail_holiday_tenant_idx"),
                ],
            },
        )

    operations.append(
        migrations.CreateModel(
            name="WeeklyAvailability",
            fields=weekly_fields,
            options={
                "ordering": ["provider", "weekday", "start_time"],
                "indexes": indexes_weekly,
            },
        )
    )
    operations.append(
        migrations.CreateModel(
            name="AvailabilityBreak",
            fields=break_fields,
            options={
                "ordering": ["provider", "weekday", "start_time"],
                "indexes": indexes_break,
            },
        )
    )
    operations.append(
        migrations.CreateModel(
            name="AvailabilityException",
            fields=exception_fields,
            options={
                "ordering": ["provider", "date"],
                "unique_together": {("provider", "date")},
                "indexes": indexes_exception,
            },
        )
    )

    if holidays_model:
        operations.append(holidays_model)

    return operations


class Migration(migrations.Migration):
    initial = True

    provider_model = getattr(settings, "AVAILABILITY_PROVIDER_MODEL", "providers.Provider")
    tenant_model = getattr(settings, "AVAILABILITY_TENANT_MODEL", None)
    has_tenant = bool(tenant_model)

    dependencies = [
        migrations.swappable_dependency(provider_model),
    ]
    if has_tenant:
        dependencies.append(migrations.swappable_dependency(tenant_model))

    operations = build_models(has_tenant, provider_model, tenant_model)
