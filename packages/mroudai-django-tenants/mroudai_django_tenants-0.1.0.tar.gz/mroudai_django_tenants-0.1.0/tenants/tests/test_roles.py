from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from tenants.models import Tenant, TenantMembership
from tenants.roles import has_role, is_admin, is_owner, require_role


class RoleHelperTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(username="owner")
        self.staff = User.objects.create_user(username="staff")
        self.tenant = Tenant.objects.create(name="Role Tenant")
        TenantMembership.objects.create(
            tenant=self.tenant, user=self.owner, role=TenantMembership.Role.OWNER
        )
        TenantMembership.objects.create(
            tenant=self.tenant, user=self.staff, role=TenantMembership.Role.STAFF
        )

    def test_is_owner_and_admin(self):
        self.assertTrue(is_owner(self.owner, self.tenant))
        self.assertTrue(is_admin(self.owner, self.tenant))
        self.assertFalse(is_owner(self.staff, self.tenant))
        self.assertFalse(is_admin(self.staff, self.tenant))

    def test_has_role(self):
        self.assertTrue(has_role(self.owner, self.tenant, TenantMembership.Role.OWNER))
        self.assertFalse(has_role(self.owner, self.tenant, TenantMembership.Role.STAFF))

    def test_require_role_raises_for_insufficient_privileges(self):
        with self.assertRaises(ValidationError):
            require_role(self.staff, self.tenant, TenantMembership.Role.ADMIN)
