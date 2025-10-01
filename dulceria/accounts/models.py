<<<<<<< HEAD
from django.db import models
from django.contrib.auth.models import User

=======
from django.conf import settings
from django.db import models
from organizations.models import Organization
>>>>>>> 04e6a5ee1fc4dece109bf9b7c90a778916ede4c7

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('employee', 'Empleado'),
        ('viewer', 'Visualizador'),
    ]

<<<<<<< HEAD
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='employee', verbose_name='Rol')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    organization = models.ForeignKey('organizations.Organization', on_delete=models.PROTECT, verbose_name='Organización')

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
=======
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
>>>>>>> 04e6a5ee1fc4dece109bf9b7c90a778916ede4c7
