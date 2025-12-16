import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from availability.models import (
    AvailabilityBreak,
    AvailabilityException,
    AvailabilityExceptionKind,
    TenantHoliday,
    WeeklyAvailability,
)
from availability.selectors import get_working_windows_for_date, is_provider_available

from .testapp.models import Provider, Tenant


class AvailabilityModelTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Tenant A")
        self.provider = Provider.objects.create(tenant=self.tenant, name="Provider A")

    def test_weekly_availability_prevents_overlap(self):
        WeeklyAvailability.objects.create(
            tenant=self.tenant,
            provider=self.provider,
            weekday=0,
            start_time=datetime.time(9, 0),
            end_time=datetime.time(12, 0),
        )
        with self.assertRaises(ValidationError):
            WeeklyAvailability.objects.create(
                tenant=self.tenant,
                provider=self.provider,
                weekday=0,
                start_time=datetime.time(11, 0),
                end_time=datetime.time(13, 0),
            )

    def test_break_overlap_prevention(self):
        AvailabilityBreak.objects.create(
            tenant=self.tenant,
            provider=self.provider,
            weekday=0,
            start_time=datetime.time(12, 0),
            end_time=datetime.time(13, 0),
        )
        with self.assertRaises(ValidationError):
            AvailabilityBreak.objects.create(
                tenant=self.tenant,
                provider=self.provider,
                weekday=0,
                start_time=datetime.time(12, 30),
                end_time=datetime.time(13, 30),
            )

    def test_exception_closed_overrides_weekly(self):
        target_date = datetime.date(2024, 1, 1)  # Monday
        WeeklyAvailability.objects.create(
            tenant=self.tenant,
            provider=self.provider,
            weekday=target_date.weekday(),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(17, 0),
        )
        AvailabilityException.objects.create(
            tenant=self.tenant,
            provider=self.provider,
            date=target_date,
            kind=AvailabilityExceptionKind.CLOSED,
        )
        windows = get_working_windows_for_date(self.provider, target_date)
        self.assertEqual(windows, [])

    def test_special_hours_replace_weekly(self):
        target_date = datetime.date(2024, 1, 1)  # Monday
        WeeklyAvailability.objects.create(
            tenant=self.tenant,
            provider=self.provider,
            weekday=target_date.weekday(),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(17, 0),
        )
        AvailabilityException.objects.create(
            tenant=self.tenant,
            provider=self.provider,
            date=target_date,
            kind=AvailabilityExceptionKind.SPECIAL_HOURS,
            start_time=datetime.time(10, 0),
            end_time=datetime.time(12, 0),
        )
        windows = get_working_windows_for_date(self.provider, target_date)
        self.assertEqual(len(windows), 1)
        self.assertEqual(windows[0][0].time(), datetime.time(10, 0))
        self.assertEqual(windows[0][1].time(), datetime.time(12, 0))

    def test_break_subtraction(self):
        target_date = datetime.date(2024, 1, 1)  # Monday
        WeeklyAvailability.objects.create(
            tenant=self.tenant,
            provider=self.provider,
            weekday=target_date.weekday(),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(17, 0),
        )
        AvailabilityBreak.objects.create(
            tenant=self.tenant,
            provider=self.provider,
            weekday=target_date.weekday(),
            start_time=datetime.time(12, 0),
            end_time=datetime.time(13, 0),
        )
        windows = get_working_windows_for_date(self.provider, target_date)
        self.assertEqual(len(windows), 2)
        first, second = windows
        self.assertEqual(first[0].time(), datetime.time(9, 0))
        self.assertEqual(first[1].time(), datetime.time(12, 0))
        self.assertEqual(second[0].time(), datetime.time(13, 0))
        self.assertEqual(second[1].time(), datetime.time(17, 0))

    def test_is_provider_available(self):
        target_date = datetime.date(2024, 1, 1)  # Monday
        WeeklyAvailability.objects.create(
            tenant=self.tenant,
            provider=self.provider,
            weekday=target_date.weekday(),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(17, 0),
        )
        AvailabilityBreak.objects.create(
            tenant=self.tenant,
            provider=self.provider,
            weekday=target_date.weekday(),
            start_time=datetime.time(12, 0),
            end_time=datetime.time(13, 0),
        )
        tz = timezone.get_current_timezone()
        morning = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time(10, 0)), tz)
        lunch = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time(12, 30)), tz)
        late = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time(16, 30)), tz)
        self.assertTrue(is_provider_available(self.provider, morning, tz=tz))
        self.assertFalse(is_provider_available(self.provider, lunch, tz=tz))
        self.assertTrue(is_provider_available(self.provider, late, tz=tz))

    def test_tenant_consistency_enforced(self):
        other_tenant = Tenant.objects.create(name="Tenant B")
        with self.assertRaises(ValidationError):
            WeeklyAvailability.objects.create(
                tenant=other_tenant,
                provider=self.provider,
                weekday=0,
                start_time=datetime.time(9, 0),
                end_time=datetime.time(12, 0),
            )

    def test_holiday_closes_date(self):
        target_date = datetime.date(2024, 1, 1)
        WeeklyAvailability.objects.create(
            tenant=self.tenant,
            provider=self.provider,
            weekday=target_date.weekday(),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(17, 0),
        )
        if TenantHoliday:
            TenantHoliday.objects.create(tenant=self.tenant, date=target_date, name="Holiday")
            windows = get_working_windows_for_date(self.provider, target_date)
            self.assertEqual(windows, [])
        else:
            self.skipTest("TenantHoliday not enabled")
