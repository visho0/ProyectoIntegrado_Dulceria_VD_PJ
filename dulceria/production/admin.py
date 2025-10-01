from django.contrib import admin
from .models import Category, Product, AlertRule, ProductAlertRule, Measurement

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

@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('device', 'value', 'unit', 'timestamp', 'created_at')
    search_fields = ('device__name', 'device__serial', 'device__zone__name', 'notes')
    list_filter = ('device__zone__organization', 'device__zone', 'device', 'timestamp', 'created_at')
    ordering = ('-timestamp',)
    list_select_related = ('device', 'device__zone', 'device__zone__organization')
    readonly_fields = ('created_at',)
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Medición', {
            'fields': ('device', 'value', 'unit', 'timestamp')
        }),
        ('Información Adicional', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'device__zone__organization'
        )