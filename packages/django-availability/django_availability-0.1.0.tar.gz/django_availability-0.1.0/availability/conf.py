from django.conf import settings


def get_provider_model():
    return getattr(settings, "AVAILABILITY_PROVIDER_MODEL", "providers.Provider")


def get_tenant_model():
    return getattr(settings, "AVAILABILITY_TENANT_MODEL", None)


def tenant_enabled():
    return bool(get_tenant_model())
