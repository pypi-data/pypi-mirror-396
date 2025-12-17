from django.test import RequestFactory, TestCase, override_settings

from tenants.middleware import TenantMiddleware
from tenants.models import Tenant
from tenants.resolution import get_tenant_from_request


class ResolutionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(TENANTS_RESOLUTION_MODE="PATH", TENANTS_PATH_PREFIX="t")
    def test_path_resolution(self):
        tenant = Tenant.objects.create(name="Path Tenant")
        request = self.factory.get(f"/t/{tenant.slug}/dashboard/")
        resolved = get_tenant_from_request(request)
        self.assertEqual(resolved, tenant)

    @override_settings(
        TENANTS_RESOLUTION_MODE="SUBDOMAIN",
        TENANTS_SUBDOMAIN_BASE="example.com",
        ALLOWED_HOSTS=[".example.com", "example.com", "testserver"],
    )
    def test_subdomain_resolution(self):
        tenant = Tenant.objects.create(name="Subdomain Tenant")
        request = self.factory.get("/", HTTP_HOST=f"{tenant.slug}.example.com")
        resolved = get_tenant_from_request(request)
        self.assertEqual(resolved, tenant)

    @override_settings(TENANTS_RESOLUTION_MODE="PATH", TENANTS_PATH_PREFIX="t")
    def test_middleware_sets_tenant(self):
        tenant = Tenant.objects.create(name="Middleware Tenant")
        middleware = TenantMiddleware(lambda req: req)
        request = self.factory.get(f"/t/{tenant.slug}/")
        response = middleware(request)
        self.assertEqual(request.tenant, tenant)
        self.assertEqual(response, request)
