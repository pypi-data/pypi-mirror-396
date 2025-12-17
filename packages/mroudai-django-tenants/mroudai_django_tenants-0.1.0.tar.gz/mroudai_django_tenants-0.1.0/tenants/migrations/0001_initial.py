import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


USER_MODEL = getattr(settings, "TENANTS_USER_MODEL", None) or settings.AUTH_USER_MODEL


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Tenant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("contact_name", models.CharField(blank=True, max_length=255)),
                ("contact_email", models.EmailField(blank=True, max_length=254)),
                ("contact_phone", models.CharField(blank=True, max_length=50)),
                ("address_line1", models.CharField(blank=True, max_length=255)),
                ("address_line2", models.CharField(blank=True, max_length=255)),
                ("city", models.CharField(blank=True, max_length=255)),
                ("country", models.CharField(blank=True, default="Trinidad and Tobago", max_length=255)),
                ("logo", models.ImageField(blank=True, null=True, upload_to="tenant_logos/")),
                ("primary_colour", models.CharField(blank=True, max_length=7)),
                ("website", models.URLField(blank=True)),
                ("timezone", models.CharField(default="America/Port_of_Spain", max_length=100)),
                ("currency", models.CharField(default="TTD", max_length=3)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="TenantMembership",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("OWNER", "Owner"), ("ADMIN", "Admin"), ("STAFF", "Staff"), ("VIEWER", "Viewer")], default="STAFF", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="tenants.tenant")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tenant_memberships", to=USER_MODEL)),
            ],
            options={
                "ordering": ("tenant", "user"),
                "unique_together": {("tenant", "user")},
            },
        ),
        migrations.CreateModel(
            name="TenantDomain",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("domain", models.CharField(max_length=255, unique=True)),
                ("is_primary", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="domains", to="tenants.tenant")),
            ],
            options={
                "ordering": ("domain",),
            },
        ),
        migrations.AddIndex(
            model_name="tenant",
            index=models.Index(fields=["slug"], name="tenants_tenant_slug_2243a5_idx"),
        ),
        migrations.AddIndex(
            model_name="tenant",
            index=models.Index(fields=["is_active"], name="tenants_tenant_is_acti_b82ab0_idx"),
        ),
        migrations.AddIndex(
            model_name="tenantmembership",
            index=models.Index(fields=["tenant", "role"], name="tenants_tenant_te_role_138fbd_idx"),
        ),
        migrations.AddIndex(
            model_name="tenantmembership",
            index=models.Index(fields=["user", "is_active"], name="tenants_tenant_us_is_ac_415536_idx"),
        ),
        migrations.AddConstraint(
            model_name="tenantdomain",
            constraint=models.UniqueConstraint(condition=models.Q(("is_primary", True)), fields=("tenant",), name="tenantdomain_primary_unique"),
        ),
    ]
