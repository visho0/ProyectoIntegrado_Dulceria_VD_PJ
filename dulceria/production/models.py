from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from accounts.models import validate_rut_chileno


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    # Identificación
    name = models.CharField(max_length=200, verbose_name='Nombre')
    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU', editable=False)
    ean_upc = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='EAN/UPC')
    description = models.TextField(blank=True, verbose_name='Descripción')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Categoría')
    marca = models.CharField(max_length=100, blank=True, verbose_name='Marca')
    modelo = models.CharField(max_length=100, blank=True, verbose_name='Modelo')
    imagen_url = models.URLField(blank=True, verbose_name='URL de imagen')
    ficha_tecnica_url = models.URLField(blank=True, verbose_name='Ficha técnica (URL)')
    
    # Precios
    costo_estandar = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='Costo Estándar')
    costo_promedio = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='Costo Promedio')
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='Precio de Venta')
    iva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('19.00'), validators=[MinValueValidator(0)], verbose_name='IVA (%)', help_text='Porcentaje de IVA')
    uom_compra = models.CharField(max_length=10, default='UN', verbose_name='Unidad de compra')
    uom_venta = models.CharField(max_length=10, default='UN', verbose_name='Unidad de venta')
    factor_conversion = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('1.0000'), validators=[MinValueValidator(Decimal('0.0001'))], verbose_name='Factor de conversión Compra/Venta')
    
    # Stock
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock Actual')
    stock_minimo = models.PositiveIntegerField(default=0, verbose_name='Stock Mínimo')
    stock_maximo = models.PositiveIntegerField(null=True, blank=True, verbose_name='Stock Máximo')
    punto_reorden = models.PositiveIntegerField(null=True, blank=True, verbose_name='Punto de Reorden')
    
    # Control especial
    es_perecible = models.BooleanField(default=False, verbose_name='Producto Perecible')
    control_por_lote = models.BooleanField(default=False, verbose_name='Control por lote')
    control_por_serie = models.BooleanField(default=False, verbose_name='Control por serie')
    
    # Fecha de vencimiento
    fecha_vencimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de Vencimiento')
    mes_vencimiento = models.PositiveIntegerField(null=True, blank=True, verbose_name='Mes de Vencimiento', help_text='Mes del año (1-12)')
    
    # Otros
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True, verbose_name='Imagen')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['name']
        # Nota: Django crea automáticamente los permisos:
        # - production.add_product
        # - production.change_product
        # - production.delete_product
        # - production.view_product

    def save(self, *args, **kwargs):
        """Generar SKU automáticamente si no existe"""
        if not self.sku:
            # Obtener el último número de SKU
            ultimo_producto = Product.objects.order_by('-id').first()
            if ultimo_producto and ultimo_producto.sku:
                try:
                    # Extraer el número del SKU (ej: SKU-001 -> 1)
                    numero = int(ultimo_producto.sku.replace('SKU-', '').replace('SKU', ''))
                except (ValueError, AttributeError):
                    numero = 0
            else:
                numero = 0
            # Generar nuevo SKU
            self.sku = f"SKU-{str(numero + 1).zfill(3)}"
        if self.punto_reorden is None:
            self.punto_reorden = self.stock_minimo
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.sku})"


class AlertRule(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]

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

    def __str__(self):
        return f"{self.product.name} - {self.alert_rule.name}"


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
        ]

    def __str__(self):
        return f"{self.device.name} - {self.value} {self.unit} ({self.timestamp})"


class Proveedor(models.Model):
    """Modelo para proveedores de la dulcería"""
    MONEDA_CHOICES = [
        ('CLP', 'Peso Chileno (CLP)'),
        ('USD', 'Dólar (USD)'),
        ('EUR', 'Euro (EUR)'),
    ]
    
    # Identificación
    rut = models.CharField(max_length=12, validators=[validate_rut_chileno], unique=True, verbose_name='RUT', help_text='Formato: 12345678-9')
    razon_social = models.CharField(max_length=200, verbose_name='Razón Social')
    nombre_fantasia = models.CharField(max_length=200, blank=True, verbose_name='Nombre de Fantasía')
    sitio_web = models.URLField(blank=True, verbose_name='Sitio web')
    
    # Datos de contacto
    email = models.EmailField(verbose_name='Correo Electrónico')
    telefono = models.CharField(max_length=30, blank=True, verbose_name='Teléfono')
    direccion = models.CharField(max_length=200, blank=True, verbose_name='Dirección')
    ciudad = models.CharField(max_length=100, blank=True, verbose_name='Ciudad')
    pais = models.CharField(max_length=100, default='Chile', verbose_name='País')
    
    # Condiciones comerciales
    plazo_pago = models.PositiveIntegerField(default=30, verbose_name='Plazo de Pago (días)', help_text='Días para el pago')
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES, default='CLP', verbose_name='Moneda')
    condiciones_pago = models.CharField(max_length=255, default='Contado', verbose_name='Condiciones de pago')
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name='Descuento (%)', help_text='Porcentaje de descuento')
    contacto_principal_nombre = models.CharField(max_length=120, blank=True, verbose_name='Contacto principal')
    contacto_principal_email = models.EmailField(blank=True, verbose_name='Email contacto')
    contacto_principal_telefono = models.CharField(max_length=30, blank=True, verbose_name='Teléfono contacto')
    estado = models.CharField(max_length=10, choices=[('ACTIVO', 'Activo'), ('BLOQUEADO', 'Bloqueado')], default='ACTIVO', verbose_name='Estado')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')
    
    # Relación con productos
    es_preferente = models.BooleanField(default=False, verbose_name='Proveedor Preferente')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    
    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['razon_social']
    
    def __str__(self):
        return f"{self.razon_social} ({self.rut})"


class ProductoProveedor(models.Model):
    """Relación entre productos y proveedores con costos y lead time"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Producto', related_name='proveedores')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, verbose_name='Proveedor', related_name='productos')
    costo = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(0)], verbose_name='Costo')
    lead_time = models.PositiveIntegerField(default=7, verbose_name='Lead Time (días)', help_text='Tiempo de entrega en días')
    min_lote = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal('1.000000'), validators=[MinValueValidator(Decimal('0.000001'))], verbose_name='Lote mínimo')
    descuento_pct = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)], verbose_name='Descuento (%)')
    es_preferente = models.BooleanField(default=False, verbose_name='Proveedor Preferente para este Producto')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    
    class Meta:
        verbose_name = 'Producto-Proveedor'
        verbose_name_plural = 'Productos-Proveedores'
        unique_together = ('product', 'proveedor')
        ordering = ['-es_preferente', 'proveedor__razon_social']
    
    def __str__(self):
        return f"{self.product.name} - {self.proveedor.razon_social}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.es_preferente:
            ProductoProveedor.objects.filter(product=self.product).exclude(pk=self.pk).update(es_preferente=False)