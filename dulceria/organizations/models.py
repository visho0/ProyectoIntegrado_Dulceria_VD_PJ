from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=120, unique=True, verbose_name="Nombre")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de eliminación")

    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"
        ordering = ['name']

    def __str__(self):
        return self.name

class Zone(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name="Organización")
    description = models.TextField(blank=True, verbose_name="Descripción")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Zona"
        verbose_name_plural = "Zonas"
        ordering = ['name']
        unique_together = ['name', 'organization']

    def __str__(self):
        return f"{self.name} - {self.organization.name}"

class Device(models.Model):
    DEVICE_STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('maintenance', 'Mantenimiento'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nombre")
    serial = models.CharField(max_length=50, unique=True, verbose_name="Número de serie")
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, verbose_name="Zona")
    status = models.CharField(max_length=20, choices=DEVICE_STATUS_CHOICES, default='active', verbose_name="Estado")
    description = models.TextField(blank=True, verbose_name="Descripción")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Dispositivo"
        verbose_name_plural = "Dispositivos"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.serial})"

    @property
    def organization(self):
        return self.zone.organization