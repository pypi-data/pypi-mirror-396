from django.contrib import admin

from .models import AvailabilityBreak, AvailabilityException, TenantHoliday, WeeklyAvailability


class CleanOnSaveMixin:
    def save_model(self, request, obj, form, change):
        obj.full_clean()
        return super().save_model(request, obj, form, change)


@admin.register(WeeklyAvailability)
class WeeklyAvailabilityAdmin(CleanOnSaveMixin, admin.ModelAdmin):
    list_display = ("provider", "weekday", "start_time", "end_time", "is_active", "tenant_display")
    ordering = ("provider", "weekday", "start_time")

    def get_list_filter(self, request):
        filters = ["weekday", "is_active"]
        if hasattr(self.model, "tenant"):
            filters.append("tenant")
        return filters

    def tenant_display(self, obj):
        return getattr(obj, "tenant", None)

    tenant_display.short_description = "Tenant"


@admin.register(AvailabilityBreak)
class AvailabilityBreakAdmin(CleanOnSaveMixin, admin.ModelAdmin):
    list_display = ("provider", "weekday", "start_time", "end_time", "is_active", "tenant_display")
    ordering = ("provider", "weekday", "start_time")

    def get_list_filter(self, request):
        filters = ["weekday", "is_active"]
        if hasattr(self.model, "tenant"):
            filters.append("tenant")
        return filters

    def tenant_display(self, obj):
        return getattr(obj, "tenant", None)

    tenant_display.short_description = "Tenant"


@admin.register(AvailabilityException)
class AvailabilityExceptionAdmin(CleanOnSaveMixin, admin.ModelAdmin):
    list_display = ("provider", "date", "kind", "start_time", "end_time", "tenant_display")
    ordering = ("provider", "date")
    date_hierarchy = "date"

    def get_list_filter(self, request):
        filters = ["kind", "date"]
        if hasattr(self.model, "tenant"):
            filters.append("tenant")
        return filters

    def tenant_display(self, obj):
        return getattr(obj, "tenant", None)

    tenant_display.short_description = "Tenant"


if "TenantHoliday" in locals():

    @admin.register(TenantHoliday)
    class TenantHolidayAdmin(CleanOnSaveMixin, admin.ModelAdmin):
        list_display = ("tenant", "date", "name")
        list_filter = ("tenant", "date")
        ordering = ("tenant", "date")
