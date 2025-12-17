# mroudai-django-tenants

Reusable Django app providing an organisation/tenant foundation for SaaS products. It tracks which tenant a request belongs to, who manages that tenant, and offers simple role helpers and admin screens. It **does not** enforce any database-per-tenant or schema-per-tenant strategy and avoids billing/subscription concerns.

## What it does
- Tenant profile with contact, address, branding, locale, and metadata fields.
- Memberships that link users to tenants with four roles: owner, admin, staff, viewer.
- Role helpers (`is_owner`, `is_admin`, `require_role`) and a lightweight service layer to manage memberships safely.
- Tenant resolution utilities for path- or subdomain-based tenancy plus optional middleware.
- Django admin UX with inlines for memberships and domains.

## What it does not do
- No billing or subscription management (pair with your subscriptions app).
- No payment integrations.
- No opinion on database-per-tenant or schema-per-tenant; bring your own multi-tenancy framework if needed.
- No fully fledged RBAC/ACL beyond the four core roles.

## Installation
```bash
pip install mroudai-django-tenants
```
Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    # ...
    "tenants",
]
```

Run migrations:
```bash
python manage.py migrate tenants
```

## Settings
```python
TENANTS_USER_MODEL = None  # defaults to AUTH_USER_MODEL
TENANTS_RESOLUTION_MODE = "PATH"  # "PATH", "SUBDOMAIN", "NONE"
TENANTS_PATH_PREFIX = "t"  # /t/<tenant_slug>/...
TENANTS_SUBDOMAIN_BASE = None  # e.g. "softwarefool.com"
TENANTS_ALLOW_PUBLIC_SIGNUP = False
TENANTS_DEFAULT_ROLE = "STAFF"  # when public signup is enabled
TENANTS_DEFAULT_TIMEZONE = "America/Port_of_Spain"
TENANTS_DEFAULT_CURRENCY = "TTD"
```

## Models
- `Tenant`: organisation profile with name, slug, contact details, address, branding, locale, metadata, and timestamps. Slug auto-generates from `name` and resolves collisions with numeric suffixes.
- `TenantMembership`: links a `user` to a `tenant` with a `role` (`OWNER`, `ADMIN`, `STAFF`, `VIEWER`) and enforces uniqueness per tenant/user.
- `TenantDomain` (optional helper): map custom domains or subdomains to tenants and flag a primary domain.

### Slug format
Tenant slugs auto-generate from the name if blank; collisions append `-1`, `-2`, etc. Primary colour values must be hex strings in the form `#RRGGBB`.

## Service layer
Located in `tenants.services`:
- `create_tenant(name, owner_user, **fields)`: creates a tenant and an owner membership atomically.
- `add_member(tenant, user, role="STAFF", actor=None)`: owners/admins may add members; prevents duplicates.
- `change_role(membership, new_role, actor=None)`: owners/admins may change roles; cannot remove the last owner.
- `remove_member(membership, actor=None)`: owners/admins may remove members; cannot remove the last owner.

All functions raise `ValidationError` on invalid operations.

## Role helpers
In `tenants.permissions` (and `tenants.roles`):
- `is_owner(user, tenant)`
- `is_admin(user, tenant)` (owners count as admins)
- `has_role(user, tenant, role)`
- `require_role(user, tenant, min_role)` – enforces the hierarchy `OWNER > ADMIN > STAFF > VIEWER`.

## Tenant resolution
Utilities live in `tenants.resolution`:
- `PATH` mode: URLs like `/t/<tenant_slug>/...` using `TENANTS_PATH_PREFIX`.
- `SUBDOMAIN` mode: `<tenant_slug>.<TENANTS_SUBDOMAIN_BASE>`.
- `NONE`: returns `None`; pass tenants explicitly.

Optional middleware `tenants.middleware.TenantMiddleware` sets `request.tenant` using `get_tenant_from_request`.

## Admin
Tenant admin lists name, slug, activity, timezone, currency, and created time. Slug prepopulates from the name. Memberships and domains are editable inline. Admin saves call `full_clean` for safer validation.

## Example usage
```python
from tenants import services
from tenants.models import TenantMembership

# Create a tenant with an owner
tenant = services.create_tenant(name="Acme Ltd", owner_user=request.user)

# Add a staff member
services.add_member(tenant=tenant, user=other_user, role=TenantMembership.Role.STAFF, actor=request.user)
```

Example path: `/t/acme/dashboard/` where `acme` is the tenant slug.

## Notes
- Designed for Django 4.2+ / 5.x and Python 3.10+.
- Tested with SQLite; PostgreSQL recommended for production.
- Uses UK spelling in docs and comments.
