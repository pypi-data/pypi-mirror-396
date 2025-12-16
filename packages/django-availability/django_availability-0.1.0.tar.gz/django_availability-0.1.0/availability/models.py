from __future__ import annotations

from typing import Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from .conf import get_provider_model, get_tenant_model, tenant_enabled


class AvailabilityExceptionKind(models.TextChoices):
    CLOSED = "closed", "Closed"
    SPECIAL_HOURS = "special_hours", "Special hours"


def validate_no_overlaps(
    provider,
    weekday: int,
    start_time,
    end_time,
    model_cls: type[models.Model],
    instance_id: Optional[int] = None,
):
    """
    Ensure no active objects overlap for the same provider + weekday.
    Overlap rule: start < other_end AND other_start < end.
    """

    filters = Q(provider=provider, weekday=weekday, is_active=True)
    if instance_id:
        filters &= ~Q(id=instance_id)

    has_tenant_field = hasattr(model_cls, "tenant")
    if has_tenant_field and hasattr(provider, "tenant"):
        filters &= Q(tenant=provider.tenant)

    overlap_filter = Q(start_time__lt=end_time, end_time__gt=start_time)
    if model_cls.objects.filter(filters & overlap_filter).exists():
        raise ValidationError("Overlapping availability entries are not allowed.")


class BaseAvailability(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def _enforce_tenant_consistency(self):
        if not tenant_enabled():
            return
        tenant_model = get_tenant_model()
        if not tenant_model:
            return
        tenant_value = getattr(self, "tenant", None)
        if tenant_value is None:
            raise ValidationError({"tenant": "Tenant is required."})
        provider = getattr(self, "provider", None)
        provider_tenant = getattr(provider, "tenant", None)
        if provider_tenant and tenant_value != provider_tenant:
            raise ValidationError("Tenant mismatch between provider and availability object.")

    def _validate_time_ordering(self, field_start: str = "start_time", field_end: str = "end_time"):
        start_time = getattr(self, field_start)
        end_time = getattr(self, field_end)
        if start_time is None or end_time is None:
            return
        if end_time <= start_time:
            raise ValidationError({field_end: "End time must be after start time."})


class WeeklyAvailability(BaseAvailability):
    provider = models.ForeignKey(get_provider_model(), on_delete=models.CASCADE, related_name="weekly_availability")
    weekday = models.IntegerField(choices=[(i, i) for i in range(7)])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    if tenant_enabled():
        tenant = models.ForeignKey(get_tenant_model(), on_delete=models.CASCADE, related_name="weekly_availability")

    class Meta:
        ordering = ["provider", "weekday", "start_time"]
        indexes = [
            models.Index(fields=["provider", "weekday", "is_active"], name="avail_weekly_active_idx"),
        ]
        if tenant_enabled():
            indexes.append(
                models.Index(
                    fields=["tenant", "provider", "weekday", "is_active"],
                    name="avail_weekly_tenant_idx",
                )
            )

    def clean(self):
        super().clean()
        self._validate_time_ordering()
        self._enforce_tenant_consistency()
        if self.is_active:
            validate_no_overlaps(
                provider=self.provider,
                weekday=self.weekday,
                start_time=self.start_time,
                end_time=self.end_time,
                model_cls=WeeklyAvailability,
                instance_id=self.pk,
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.provider} - {self.weekday} {self.start_time}-{self.end_time}"


class AvailabilityBreak(BaseAvailability):
    provider = models.ForeignKey(get_provider_model(), on_delete=models.CASCADE, related_name="availability_breaks")
    weekday = models.IntegerField(choices=[(i, i) for i in range(7)])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    if tenant_enabled():
        tenant = models.ForeignKey(get_tenant_model(), on_delete=models.CASCADE, related_name="availability_breaks")

    class Meta:
        ordering = ["provider", "weekday", "start_time"]
        indexes = [
            models.Index(fields=["provider", "weekday", "is_active"], name="avail_break_active_idx"),
        ]
        if tenant_enabled():
            indexes.append(
                models.Index(
                    fields=["tenant", "provider", "weekday", "is_active"],
                    name="avail_break_tenant_idx",
                )
            )

    def clean(self):
        super().clean()
        self._validate_time_ordering()
        self._enforce_tenant_consistency()
        if self.is_active:
            validate_no_overlaps(
                provider=self.provider,
                weekday=self.weekday,
                start_time=self.start_time,
                end_time=self.end_time,
                model_cls=AvailabilityBreak,
                instance_id=self.pk,
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.provider} break {self.weekday} {self.start_time}-{self.end_time}"


class AvailabilityException(BaseAvailability):
    provider = models.ForeignKey(get_provider_model(), on_delete=models.CASCADE, related_name="availability_exceptions")
    date = models.DateField()
    kind = models.CharField(max_length=32, choices=AvailabilityExceptionKind.choices)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)

    if tenant_enabled():
        tenant = models.ForeignKey(get_tenant_model(), on_delete=models.CASCADE, related_name="availability_exceptions")

    class Meta:
        ordering = ["provider", "date"]
        unique_together = [("provider", "date")]
        indexes = [
            models.Index(fields=["provider", "date"], name="avail_exc_provider_date_idx"),
        ]
        if tenant_enabled():
            indexes.append(
                models.Index(fields=["tenant", "provider", "date"], name="avail_exc_tenant_date_idx")
            )

    def clean(self):
        super().clean()
        self._enforce_tenant_consistency()
        if self.kind == AvailabilityExceptionKind.CLOSED:
            if self.start_time or self.end_time:
                raise ValidationError("Closed exceptions cannot define start/end times.")
        elif self.kind == AvailabilityExceptionKind.SPECIAL_HOURS:
            if self.start_time is None or self.end_time is None:
                raise ValidationError("Special hours require start and end times.")
            self._validate_time_ordering()
        else:
            raise ValidationError("Invalid exception kind.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.provider} {self.date} ({self.get_kind_display()})"


if tenant_enabled():

    class TenantHoliday(BaseAvailability):
        date = models.DateField()
        name = models.CharField(max_length=255, blank=True)
        tenant = models.ForeignKey(get_tenant_model(), on_delete=models.CASCADE, related_name="availability_holidays")

        class Meta:
            ordering = ["date"]
            unique_together = [("tenant", "date")]
            indexes = [
                models.Index(fields=["tenant", "date"], name="avail_holiday_tenant_idx"),
            ]

        def clean(self):
            super().clean()
            if self.tenant is None:
                raise ValidationError({"tenant": "Tenant is required."})

        def save(self, *args, **kwargs):
            self.full_clean()
            return super().save(*args, **kwargs)

        def __str__(self):
            name = f" - {self.name}" if self.name else ""
            return f"{self.date}{name}"
