from .resolution import get_tenant_from_request


class TenantMiddleware:
    """
    Optional middleware that attaches the resolved tenant to the request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = get_tenant_from_request(request)
        return self.get_response(request)
