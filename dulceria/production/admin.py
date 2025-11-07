from django.contrib import admin
from .models import Category, Product, AlertRule, ProductAlertRule, Bodega, MovimientoInventario, Proveedor, ProductoProveedor
# Measurement y Device no se usan - comentado
# from .models import Measurement

class ProductAlertRuleInline(admin.TabularInline):
    model = ProductAlertRule
    extra = 0
    fields = ('alert_rule', 'min_threshold', 'max_threshold', 'is_active')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'stock', 'is_active', 'created_at')
    search_fields = ('name', 'sku', 'description')
    list_filter = ('category', 'is_active', 'created_at', 'updated_at')
    ordering = ('name',)
    list_select_related = ('category',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductAlertRuleInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'sku', 'category', 'description')
        }),
        ('Precio y Stock', {
            'fields': ('price', 'stock', 'is_active')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'severity', 'min_threshold', 'max_threshold', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('severity', 'is_active', 'created_at', 'updated_at')
    ordering = ('severity', 'name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Configuración de Alertas', {
            'fields': ('severity', 'min_threshold', 'max_threshold')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProductAlertRule)
class ProductAlertRuleAdmin(admin.ModelAdmin):
    list_display = ('product', 'alert_rule', 'min_threshold', 'max_threshold', 'is_active', 'created_at')
    search_fields = ('product__name', 'product__sku', 'alert_rule__name')
    list_filter = ('alert_rule__severity', 'is_active', 'created_at', 'updated_at')
    ordering = ('product__name', 'alert_rule__severity')
    list_select_related = ('product', 'alert_rule', 'product__category')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Relación', {
            'fields': ('product', 'alert_rule')
        }),
        ('Umbrales', {
            'fields': ('min_threshold', 'max_threshold', 'is_active')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'is_active', 'created_at')
    search_fields = ('codigo', 'nombre', 'descripcion')
    list_filter = ('is_active', 'created_at', 'updated_at')
    ordering = ('codigo',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tipo', 'producto', 'bodega', 'cantidad', 'proveedor', 'doc_referencia', 'created_at')
    search_fields = ('producto__sku', 'producto__name', 'proveedor__razon_social', 'doc_referencia', 'lote', 'serie')
    list_filter = ('tipo', 'bodega', 'fecha', 'created_at')
    ordering = ('-fecha', '-created_at')
    list_select_related = ('producto', 'proveedor', 'bodega', 'creado_por')
    readonly_fields = ('created_at', 'updated_at', 'creado_por')
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Datos del Movimiento', {
            'fields': ('fecha', 'tipo', 'producto', 'proveedor', 'bodega', 'cantidad')
        }),
        ('Control Avanzado', {
            'fields': ('lote', 'serie', 'fecha_vencimiento'),
            'classes': ('collapse',)
        }),
        ('Referencias y Observaciones', {
            'fields': ('doc_referencia', 'observaciones', 'motivo'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('creado_por', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es nuevo
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('rut', 'razon_social', 'nombre_fantasia', 'email', 'estado', 'created_at')
    search_fields = ('rut', 'razon_social', 'nombre_fantasia', 'email')
    list_filter = ('estado', 'moneda', 'created_at')
    ordering = ('razon_social',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ProductoProveedor)
class ProductoProveedorAdmin(admin.ModelAdmin):
    list_display = ('product', 'proveedor', 'costo', 'lead_time', 'es_preferente', 'created_at')
    search_fields = ('product__name', 'product__sku', 'proveedor__razon_social')
    list_filter = ('es_preferente', 'created_at')
    ordering = ('-es_preferente', 'proveedor__razon_social')
    list_select_related = ('product', 'proveedor')
    readonly_fields = ('created_at', 'updated_at')