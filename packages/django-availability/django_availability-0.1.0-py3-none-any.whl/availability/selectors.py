from __future__ import annotations

from datetime import date as date_cls, datetime, timedelta, time as time_cls
from typing import Dict, List, Sequence, Tuple

from django.db.models import Q
from django.utils import timezone

from . import models as availability_models
from .conf import tenant_enabled

AvailabilityBreak = availability_models.AvailabilityBreak
AvailabilityException = availability_models.AvailabilityException
AvailabilityExceptionKind = availability_models.AvailabilityExceptionKind
WeeklyAvailability = availability_models.WeeklyAvailability
validate_no_overlaps = availability_models.validate_no_overlaps
TenantHoliday = getattr(availability_models, "TenantHoliday", None)

TimeWindow = Tuple[time_cls, time_cls]
DateTimeWindow = Tuple[datetime, datetime]


def _get_timezone(tz=None):
    if tz:
        return tz
    return timezone.get_current_timezone()


def _get_tenant_for_provider(provider):
    if not tenant_enabled():
        return None
    return getattr(provider, "tenant", None)


def _subtract_breaks(windows: Sequence[TimeWindow], breaks: Sequence[TimeWindow]) -> List[TimeWindow]:
    result: List[TimeWindow] = []
    for window_start, window_end in windows:
        current_segments = [(window_start, window_end)]
        for break_start, break_end in breaks:
            next_segments: List[TimeWindow] = []
            for seg_start, seg_end in current_segments:
                if break_end <= seg_start or break_start >= seg_end:
                    next_segments.append((seg_start, seg_end))
                    continue
                if break_start > seg_start:
                    next_segments.append((seg_start, break_start))
                if break_end < seg_end:
                    next_segments.append((break_end, seg_end))
            current_segments = next_segments
        result.extend(current_segments)
    return [(start, end) for start, end in result if start < end]


def _to_aware_datetime(target_date: date_cls, t: time_cls, tz):
    combined = datetime.combine(target_date, t)
    if timezone.is_naive(combined):
        return timezone.make_aware(combined, tz)
    return combined.astimezone(tz)


def _get_weekly_windows(provider, weekday: int, tenant=None) -> List[TimeWindow]:
    filters = Q(provider=provider, weekday=weekday, is_active=True)
    if tenant_enabled() and tenant is not None and hasattr(WeeklyAvailability, "tenant"):
        filters &= Q(tenant=tenant)
    qs = WeeklyAvailability.objects.filter(filters).order_by("sort_order", "start_time")
    return [(obj.start_time, obj.end_time) for obj in qs]


def _get_breaks(provider, weekday: int, tenant=None) -> List[TimeWindow]:
    filters = Q(provider=provider, weekday=weekday, is_active=True)
    if tenant_enabled() and tenant is not None and hasattr(AvailabilityBreak, "tenant"):
        filters &= Q(tenant=tenant)
    qs = AvailabilityBreak.objects.filter(filters).order_by("start_time")
    return [(obj.start_time, obj.end_time) for obj in qs]


def _get_exception(provider, target_date: date_cls, tenant=None):
    filters = Q(provider=provider, date=target_date)
    if tenant_enabled() and tenant is not None and hasattr(AvailabilityException, "tenant"):
        filters &= Q(tenant=tenant)
    return AvailabilityException.objects.filter(filters).first()


def _is_holiday(tenant, target_date: date_cls) -> bool:
    if not tenant_enabled():
        return False
    if tenant is None or TenantHoliday is None:
        return False
    filters = Q(tenant=tenant, date=target_date)
    return TenantHoliday.objects.filter(filters).exists()


def get_working_windows_for_date(provider, target_date: date_cls, tz=None) -> List[DateTimeWindow]:
    tz = _get_timezone(tz)
    tenant = _get_tenant_for_provider(provider)
    weekday = target_date.weekday()

    if _is_holiday(tenant, target_date):
        return []

    exception = _get_exception(provider, target_date, tenant)
    if exception:
        if exception.kind == AvailabilityExceptionKind.CLOSED:
            return []
        if exception.kind == AvailabilityExceptionKind.SPECIAL_HOURS and exception.start_time and exception.end_time:
            windows: List[TimeWindow] = [(exception.start_time, exception.end_time)]
        else:
            windows = []
    else:
        windows = _get_weekly_windows(provider, weekday, tenant)

    if not windows:
        return []

    breaks = _get_breaks(provider, weekday, tenant)
    final_windows = _subtract_breaks(windows, breaks)

    aware_windows: List[DateTimeWindow] = []
    for start_time, end_time in final_windows:
        start_dt = _to_aware_datetime(target_date, start_time, tz)
        end_dt = _to_aware_datetime(target_date, end_time, tz)
        aware_windows.append((start_dt, end_dt))
    return aware_windows


def get_working_windows(provider, start_date: date_cls, end_date: date_cls, tz=None) -> Dict[date_cls, List[DateTimeWindow]]:
    if end_date < start_date:
        raise ValueError("end_date must be on or after start_date.")
    delta = (end_date - start_date).days
    results: Dict[date_cls, List[DateTimeWindow]] = {}
    for offset in range(delta + 1):
        current_date = start_date + timedelta(days=offset)
        results[current_date] = get_working_windows_for_date(provider, current_date, tz=tz)
    return results


def is_provider_available(provider, dt: datetime, tz=None) -> bool:
    tz = _get_timezone(tz)
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, tz)
    local_dt = dt.astimezone(tz)
    windows = get_working_windows_for_date(provider, local_dt.date(), tz=tz)
    for start_dt, end_dt in windows:
        if start_dt <= local_dt < end_dt:
            return True
    return False


__all__ = [
    "get_working_windows_for_date",
    "get_working_windows",
    "is_provider_available",
    "validate_no_overlaps",
    "AvailabilityExceptionKind",
]
