from typing import Optional

from django.conf import settings

from .models import Tenant


def _get_setting(name: str, default):
    return getattr(settings, name, default)


def _tenant_by_slug(slug: str) -> Optional[Tenant]:
    if not slug:
        return None
    return Tenant.objects.filter(slug=slug).first()


def _resolve_from_path(request) -> Optional[Tenant]:
    prefix = _get_setting("TENANTS_PATH_PREFIX", "t").strip("/")
    if not prefix:
        return None

    path = request.path or ""
    segments = path.lstrip("/").split("/")
    if len(segments) >= 2 and segments[0] == prefix:
        return _tenant_by_slug(segments[1])
    return None


def _resolve_from_subdomain(request) -> Optional[Tenant]:
    base_domain = _get_setting("TENANTS_SUBDOMAIN_BASE", None)
    if not base_domain:
        return None

    host = (request.get_host() or "").split(":")[0]
    if not host or not host.endswith(base_domain):
        return None

    # Strip the base domain and trailing dot.
    slug_part = host[: -len(base_domain)]
    slug_part = slug_part[:-1] if slug_part.endswith(".") else slug_part
    if not slug_part:
        return None
    slug = slug_part.split(".")[0]
    return _tenant_by_slug(slug)


def get_tenant_from_request(request) -> Optional[Tenant]:
    """
    Resolve a tenant from the incoming request based on settings.
    """
    mode = _get_setting("TENANTS_RESOLUTION_MODE", "PATH")
    if mode == "NONE":
        return None
    if mode == "PATH":
        return _resolve_from_path(request)
    if mode == "SUBDOMAIN":
        return _resolve_from_subdomain(request)
    return None
