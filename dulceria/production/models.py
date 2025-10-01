from django.db import models
from organizations.models import Organization, Zone, Device

<<<<<<< HEAD

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
=======
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
>>>>>>> 04e6a5ee1fc4dece109bf9b7c90a778916ede4c7
        ordering = ['name']

    def __str__(self):
        return self.name

<<<<<<< HEAD

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Nombre')
    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU')
    description = models.TextField(blank=True, verbose_name='Descripción')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Categoría')

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
=======
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Categoría")
    description = models.TextField(blank=True, verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
>>>>>>> 04e6a5ee1fc4dece109bf9b7c90a778916ede4c7
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.sku})"

<<<<<<< HEAD

=======
>>>>>>> 04e6a5ee1fc4dece109bf9b7c90a778916ede4c7
class AlertRule(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]

<<<<<<< HEAD
    name = models.CharField(max_length=100, verbose_name='Nombre')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, verbose_name='Severidad')
    min_threshold = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Umbral mínimo')
    max_threshold = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Umbral máximo')
    description = models.TextField(blank=True, verbose_name='Descripción')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')

    class Meta:
        verbose_name = 'Regla de Alerta'
        verbose_name_plural = 'Reglas de Alerta'
        ordering = ['severity', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_severity_display()})"


class ProductAlertRule(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Producto')
    alert_rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, verbose_name='Regla de Alerta')
    min_threshold = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Umbral mínimo')
    max_threshold = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Umbral máximo')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')

    class Meta:
        verbose_name = 'Regla de Alerta de Producto'
        verbose_name_plural = 'Reglas de Alerta de Producto'
        ordering = ['product__name', 'alert_rule__severity']
        unique_together = ('product', 'alert_rule')
=======
    name = models.CharField(max_length=100, verbose_name="Nombre")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, verbose_name="Severidad")
    min_threshold = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Umbral mínimo")
    max_threshold = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Umbral máximo")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Regla de Alerta"
        verbose_name_plural = "Reglas de Alerta"
        ordering = ['severity', 'name']

    def __str__(self):
        return f"{self.name} ({self.severity})"

class ProductAlertRule(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    alert_rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, verbose_name="Regla de Alerta")
    min_threshold = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Umbral mínimo")
    max_threshold = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Umbral máximo")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Regla de Alerta de Producto"
        verbose_name_plural = "Reglas de Alerta de Producto"
        unique_together = ['product', 'alert_rule']
        ordering = ['product__name', 'alert_rule__severity']
>>>>>>> 04e6a5ee1fc4dece109bf9b7c90a778916ede4c7

    def __str__(self):
        return f"{self.product.name} - {self.alert_rule.name}"

<<<<<<< HEAD

class Measurement(models.Model):
    device = models.ForeignKey('organizations.Device', on_delete=models.CASCADE, verbose_name='Dispositivo')
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor')
    unit = models.CharField(max_length=20, default='unidad', verbose_name='Unidad')
    timestamp = models.DateTimeField(verbose_name='Fecha y hora')
    notes = models.TextField(blank=True, verbose_name='Notas')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

    class Meta:
        verbose_name = 'Medición'
        verbose_name_plural = 'Mediciones'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp'], name='prod_meas_timestamp_idx'),
            models.Index(fields=['device', 'timestamp'], name='prod_meas_dev_time_idx'),
=======
class Measurement(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name="Dispositivo")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    unit = models.CharField(max_length=20, default="unidad", verbose_name="Unidad")
    timestamp = models.DateTimeField(verbose_name="Fecha y hora")
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Medición"
        verbose_name_plural = "Mediciones"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['device', 'timestamp']),
>>>>>>> 04e6a5ee1fc4dece109bf9b7c90a778916ede4c7
        ]

    def __str__(self):
        return f"{self.device.name} - {self.value} {self.unit} ({self.timestamp})"