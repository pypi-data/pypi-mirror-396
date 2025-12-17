import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


def tenant_user_model() -> str:
    """
    Resolve the user model for the tenant membership. Falls back to AUTH_USER_MODEL.
    """
    return getattr(settings, "TENANTS_USER_MODEL", None) or settings.AUTH_USER_MODEL


def default_timezone() -> str:
    return getattr(settings, "TENANTS_DEFAULT_TIMEZONE", "America/Port_of_Spain")


def default_currency() -> str:
    return getattr(settings, "TENANTS_DEFAULT_CURRENCY", "TTD")


class Tenant(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    contact_name = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)

    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True, default="Trinidad and Tobago")

    logo = models.ImageField(upload_to="tenant_logos/", blank=True, null=True)
    primary_colour = models.CharField(max_length=7, blank=True)
    website = models.URLField(blank=True)

    timezone = models.CharField(max_length=100, default=default_timezone)
    currency = models.CharField(max_length=3, default=default_currency)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        if self.primary_colour and not re.fullmatch(r"#[0-9A-Fa-f]{6}", self.primary_colour):
            raise ValidationError(
                {"primary_colour": "Primary colour must be a hex string in the format #RRGGBB."}
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        self.full_clean()
        return super().save(*args, **kwargs)

    def _generate_unique_slug(self) -> str:
        base_slug = slugify(self.name) or "tenant"
        slug_candidate = base_slug
        counter = 1
        while Tenant.objects.exclude(pk=self.pk).filter(slug=slug_candidate).exists():
            slug_candidate = f"{base_slug}-{counter}"
            counter += 1
        return slug_candidate


class TenantMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        ADMIN = "ADMIN", "Admin"
        STAFF = "STAFF", "Staff"
        VIEWER = "VIEWER", "Viewer"

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="memberships", db_index=True
    )
    user = models.ForeignKey(
        tenant_user_model(),
        on_delete=models.CASCADE,
        related_name="tenant_memberships",
        db_index=True,
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STAFF)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("tenant", "user")
        ordering = ("tenant", "user")
        indexes = [
            models.Index(fields=["tenant", "role"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} in {self.tenant} as {self.role}"


class TenantDomain(models.Model):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="domains", db_index=True
    )
    domain = models.CharField(max_length=255, unique=True)
    is_primary = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("domain",)
        constraints = [
            models.UniqueConstraint(
                fields=["tenant"],
                condition=models.Q(is_primary=True),
                name="tenantdomain_primary_unique",
            )
        ]

    def __str__(self) -> str:
        return self.domain
