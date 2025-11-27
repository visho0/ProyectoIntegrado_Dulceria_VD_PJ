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
    
    # Aprobación de productos
    ESTADO_APROBACION_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    estado_aprobacion = models.CharField(
        max_length=20,
        choices=ESTADO_APROBACION_CHOICES,
        default='PENDIENTE',
        verbose_name='Estado de Aprobación'
    )
    aprobado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_aprobados',
        verbose_name='Aprobado por'
    )
    fecha_aprobacion = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Aprobación')
    creado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_creados',
        verbose_name='Creado por'
    )
    
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
    lead_time = models.PositiveIntegerField(default=7, verbose_name='Tiempo de Entrega (días)', help_text='Tiempo de entrega en días')
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


class Bodega(models.Model):
    """Modelo para bodegas/almacenes"""
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código', help_text='Ej: BOD-CENTRAL')
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    direccion = models.CharField(max_length=255, blank=True, verbose_name='Dirección')
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    
    class Meta:
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class MovimientoInventario(models.Model):
    """Modelo para movimientos de inventario"""
    TIPO_MOVIMIENTO_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
        ('devolucion', 'Devolución'),
        ('transferencia', 'Transferencia'),
    ]
    
    # Datos básicos del movimiento
    fecha = models.DateTimeField(verbose_name='Fecha y Hora')
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO_CHOICES, verbose_name='Tipo de Movimiento')
    producto = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Producto', related_name='movimientos')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Proveedor', related_name='movimientos')
    bodega = models.ForeignKey(Bodega, on_delete=models.PROTECT, verbose_name='Bodega', related_name='movimientos')
    cantidad = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Cantidad')
    
    # Control avanzado
    lote = models.CharField(max_length=50, blank=True, verbose_name='Lote', help_text='Número de lote')
    serie = models.CharField(max_length=50, blank=True, verbose_name='Serie', help_text='Número de serie')
    fecha_vencimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de Vencimiento')
    
    # Referencias y observaciones
    doc_referencia = models.CharField(max_length=100, blank=True, verbose_name='Documento de Referencia', help_text='OC-123 / FAC-456 / GUIA-789')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones', help_text='Notas de operación, recibo, daño, etc.')
    motivo = models.CharField(max_length=255, blank=True, verbose_name='Motivo', help_text='Diferencia inventario, devolución cliente, etc.')
    
    # Auditoría
    creado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_creados', verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    
    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha', '-created_at']
        indexes = [
            models.Index(fields=['-fecha'], name='mov_fecha_idx'),
            models.Index(fields=['producto', '-fecha'], name='mov_prod_fecha_idx'),
            models.Index(fields=['bodega', '-fecha'], name='mov_bod_fecha_idx'),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.sku} - {self.cantidad} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        """Actualizar stock del producto al guardar el movimiento"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Actualizar stock según el tipo de movimiento
            cantidad_int = int(float(self.cantidad))
            if self.tipo == 'ingreso':
                self.producto.stock += cantidad_int
            elif self.tipo == 'salida':
                self.producto.stock = max(0, self.producto.stock - cantidad_int)
            elif self.tipo == 'ajuste':
                # Los ajustes pueden ser positivos o negativos según la cantidad
                self.producto.stock = max(0, self.producto.stock + cantidad_int)
            elif self.tipo == 'devolucion':
                self.producto.stock += cantidad_int
            # Transferencias no afectan el stock total, solo entre bodegas
            
            self.producto.save(update_fields=['stock'])
    
    def delete(self, *args, **kwargs):
        """Revertir el stock al eliminar un movimiento"""
        # Revertir el cambio en el stock
        cantidad_int = int(float(self.cantidad))
        if self.tipo == 'ingreso':
            self.producto.stock = max(0, self.producto.stock - cantidad_int)
        elif self.tipo == 'salida':
            self.producto.stock += cantidad_int
        elif self.tipo == 'ajuste':
            self.producto.stock = max(0, self.producto.stock - cantidad_int)
        elif self.tipo == 'devolucion':
            self.producto.stock = max(0, self.producto.stock - cantidad_int)
        
        self.producto.save(update_fields=['stock'])
        super().delete(*args, **kwargs)