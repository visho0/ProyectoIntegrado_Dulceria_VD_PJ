from django.conf import settings
from django.db import models
from organizations.models import Organization

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('employee', 'Empleado'),
        ('viewer', 'Visualizador'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuario")
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name="Organización")
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='employee', verbose_name="Rol")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.username} @ {self.organization.name}"