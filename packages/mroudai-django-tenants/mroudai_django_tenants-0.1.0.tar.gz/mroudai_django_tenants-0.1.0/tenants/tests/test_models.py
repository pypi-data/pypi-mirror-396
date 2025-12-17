from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from tenants.models import Tenant, TenantMembership


class TenantModelTests(TestCase):
    def test_slug_generated_from_name(self):
        tenant = Tenant.objects.create(name="Acme Org")
        self.assertEqual(tenant.slug, "acme-org")

    def test_slug_collision_adds_suffix(self):
        Tenant.objects.create(name="Acme Org")
        duplicate = Tenant.objects.create(name="Acme Org")
        self.assertEqual(duplicate.slug, "acme-org-1")


class MembershipModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="user1", email="u1@example.com")
        self.tenant = Tenant.objects.create(name="Test Tenant")

    def test_membership_uniqueness(self):
        TenantMembership.objects.create(
            tenant=self.tenant,
            user=self.user,
            role=TenantMembership.Role.STAFF,
        )

        duplicate = TenantMembership(
            tenant=self.tenant,
            user=self.user,
            role=TenantMembership.Role.ADMIN,
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()
