from django.db import models

<<<<<<< HEAD

class Organization(models.Model):
    name = models.CharField(max_length=120, unique=True, verbose_name='Nombre')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de eliminación')

    class Meta:
        verbose_name = 'Organización'
        verbose_name_plural = 'Organizaciones'
=======
class Organization(models.Model):
    name = models.CharField(max_length=120, unique=True, verbose_name="Nombre")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de eliminación")

    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"
>>>>>>> 04e6a5ee1fc4dece109bf9b7c90a778916ede4c7
        ordering = ['name']

    def __str__(self):
        return self.name

<<<<<<< HEAD

class Zone(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name='Organización')

    class Meta:
        verbose_name = 'Zona'
        verbose_name_plural = 'Zonas'
        ordering = ['name']
        unique_together = ('name', 'organization')
=======
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
>>>>>>> 04e6a5ee1fc4dece109bf9b7c90a778916ede4c7

    def __str__(self):
        return f"{self.name} - {self.organization.name}"

<<<<<<< HEAD

class Device(models.Model):
    STATUS_CHOICES = [
=======
class Device(models.Model):
    DEVICE_STATUS_CHOICES = [
>>>>>>> 04e6a5ee1fc4dece109bf9b7c90a778916ede4c7
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('maintenance', 'Mantenimiento'),
    ]

<<<<<<< HEAD
    name = models.CharField(max_length=100, verbose_name='Nombre')
    serial = models.CharField(max_length=50, unique=True, verbose_name='Número de serie')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Estado')
    description = models.TextField(blank=True, verbose_name='Descripción')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, verbose_name='Zona')

    class Meta:
        verbose_name = 'Dispositivo'
        verbose_name_plural = 'Dispositivos'
=======
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
>>>>>>> 04e6a5ee1fc4dece109bf9b7c90a778916ede4c7
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.serial})"
<<<<<<< HEAD
=======

    @property
    def organization(self):
        return self.zone.organization
>>>>>>> 04e6a5ee1fc4dece109bf9b7c90a778916ede4c7
