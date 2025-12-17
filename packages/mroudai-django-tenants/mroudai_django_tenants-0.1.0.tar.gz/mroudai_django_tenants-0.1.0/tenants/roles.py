from django.core.exceptions import ValidationError

from .models import TenantMembership

ROLE_HIERARCHY = {
    TenantMembership.Role.VIEWER: 1,
    TenantMembership.Role.STAFF: 2,
    TenantMembership.Role.ADMIN: 3,
    TenantMembership.Role.OWNER: 4,
}


def _membership_for(user, tenant):
    if user is None or not getattr(user, "is_authenticated", False):
        return None
    return TenantMembership.objects.filter(
        tenant=tenant, user=user, is_active=True
    ).first()


def role_value(role: str) -> int:
    return ROLE_HIERARCHY.get(role, 0)


def has_role(user, tenant, role: str) -> bool:
    membership = _membership_for(user, tenant)
    return bool(membership and membership.role == role)


def _has_min_role(user, tenant, min_role: str) -> bool:
    membership = _membership_for(user, tenant)
    if not membership:
        return False
    return role_value(membership.role) >= role_value(min_role)


def is_owner(user, tenant) -> bool:
    return has_role(user, tenant, TenantMembership.Role.OWNER)


def is_admin(user, tenant) -> bool:
    return _has_min_role(user, tenant, TenantMembership.Role.ADMIN)


def require_role(user, tenant, min_role: str):
    """
    Ensure the user has at least the required role for the tenant.
    Raises ValidationError when the requirement is not met.
    """
    if min_role not in TenantMembership.Role.values:
        raise ValidationError(f"Unknown role '{min_role}'.")

    if not _has_min_role(user, tenant, min_role):
        raise ValidationError(
            "User does not have the required role for this tenant."
        )
    return _membership_for(user, tenant)


__all__ = [
    "ROLE_HIERARCHY",
    "has_role",
    "is_owner",
    "is_admin",
    "require_role",
    "role_value",
]
