from django.conf import settings
from django.db import models
from django.utils import timezone

from .validators import validate_rut


class Company(models.Model):
    name = models.CharField(max_length=255)
    rut = models.CharField(max_length=20, unique=True, validators=[validate_rut])
    created_at = models.DateTimeField(auto_now_add=True)
    administrators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='admin_companies',
        help_text='Usuarios con rol de administrador asociados a la empresa.',
    )

    def __str__(self):
        return self.name


class Subscription(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_CANCELLED = 'cancelled'
    STATUS_EXPIRED = 'expired'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Activa'),
        (STATUS_CANCELLED, 'Cancelada'),
        (STATUS_EXPIRED, 'Expirada'),
    ]

    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey('core.Plan', on_delete=models.PROTECT, related_name='subscriptions', null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    canceled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        plan_name = self.plan.name if self.plan else 'Sin plan'
        return f"{self.company} - {plan_name}"

    @property
    def is_active(self):
        today = timezone.now().date()
        if self.status != self.STATUS_ACTIVE:
            return False
        return self.start_date <= today <= self.end_date

    @property
    def branch_limit(self):
        if not self.is_active or not self.plan:
            return 0
        return self.plan.branch_limit

    def reports_enabled(self):
        return bool(self.is_active and self.plan and self.plan.has_feature('reports'))

    def cancel(self):
        if self.status != self.STATUS_CANCELLED:
            self.status = self.STATUS_CANCELLED
            self.canceled_at = timezone.now()
            self.save(update_fields=['status', 'canceled_at'])


class PlanFeature(models.Model):
    code = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return self.label


class Plan(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    branch_limit = models.PositiveIntegerField(null=True, blank=True, help_text='Límite de sucursales (vacío para ilimitado)')
    features = models.ManyToManyField(PlanFeature, related_name='plans', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['monthly_price', 'name']

    def __str__(self):
        return self.name

    def has_feature(self, code: str) -> bool:
        return self.features.filter(code=code).exists()
