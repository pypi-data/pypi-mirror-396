from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from tenants import services
from tenants.models import Tenant, TenantMembership


class ServiceLayerTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(username="owner")
        self.tenant = Tenant.objects.create(name="Service Tenant")
        self.owner_membership = TenantMembership.objects.create(
            tenant=self.tenant, user=self.owner, role=TenantMembership.Role.OWNER
        )

    def test_prevent_removing_last_owner(self):
        with self.assertRaises(ValidationError):
            services.remove_member(membership=self.owner_membership, actor=self.owner)

    def test_prevent_downgrading_last_owner(self):
        with self.assertRaises(ValidationError):
            services.change_role(
                membership=self.owner_membership,
                new_role=TenantMembership.Role.ADMIN,
                actor=self.owner,
            )
