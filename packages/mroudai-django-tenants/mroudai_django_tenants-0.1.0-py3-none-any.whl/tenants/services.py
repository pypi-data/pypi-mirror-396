from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Tenant, TenantMembership
from .roles import require_role


@transaction.atomic
def create_tenant(*, name, owner_user, **fields) -> Tenant:
    """
    Create a tenant along with its owner membership.
    """
    if owner_user is None:
        raise ValidationError("Owner user is required to create a tenant.")

    tenant = Tenant(name=name, **fields)
    tenant.full_clean()
    tenant.save()

    membership = TenantMembership(
        tenant=tenant, user=owner_user, role=TenantMembership.Role.OWNER
    )
    membership.full_clean()
    membership.save()
    return tenant


def _default_role() -> str:
    return getattr(settings, "TENANTS_DEFAULT_ROLE", TenantMembership.Role.STAFF)


def _validate_role(role: str) -> None:
    if role not in TenantMembership.Role.values:
        raise ValidationError(f"Invalid role '{role}'.")


def _owner_count(tenant: Tenant) -> int:
    return TenantMembership.objects.filter(
        tenant=tenant,
        role=TenantMembership.Role.OWNER,
        is_active=True,
    ).count()


def _assert_actor_can_manage(actor, tenant: Tenant) -> None:
    """
    Owners and admins may manage memberships.
    """
    if actor is None:
        return
    require_role(actor, tenant, TenantMembership.Role.ADMIN)


@transaction.atomic
def add_member(*, tenant: Tenant, user, role: str = None, actor=None) -> TenantMembership:
    role_to_use = role or _default_role()
    _validate_role(role_to_use)
    _assert_actor_can_manage(actor, tenant)

    if TenantMembership.objects.filter(tenant=tenant, user=user).exists():
        raise ValidationError("User is already a member of this tenant.")

    membership = TenantMembership(tenant=tenant, user=user, role=role_to_use)
    membership.full_clean()
    membership.save()
    return membership


@transaction.atomic
def change_role(*, membership: TenantMembership, new_role: str, actor=None) -> TenantMembership:
    _validate_role(new_role)
    _assert_actor_can_manage(actor, membership.tenant)

    if membership.role == TenantMembership.Role.OWNER and new_role != TenantMembership.Role.OWNER:
        if _owner_count(membership.tenant) <= 1:
            raise ValidationError("Cannot remove the last owner from a tenant.")

    membership.role = new_role
    membership.full_clean()
    membership.save(update_fields=["role", "updated_at"])
    return membership


@transaction.atomic
def remove_member(*, membership: TenantMembership, actor=None) -> None:
    _assert_actor_can_manage(actor, membership.tenant)

    if membership.role == TenantMembership.Role.OWNER and _owner_count(membership.tenant) <= 1:
        raise ValidationError("Cannot remove the last owner from a tenant.")

    membership.delete()
