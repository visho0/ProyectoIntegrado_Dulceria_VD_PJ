"""
Signals para auditoría automática de eventos críticos
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile, ProveedorUser, Cliente
from production.models import Product, Proveedor, MovimientoInventario
import json


def serialize_model(obj):
    """Serializar un modelo a diccionario JSON"""
    if obj is None:
        return None
    
    data = {}
    for field in obj._meta.fields:
        value = getattr(obj, field.name, None)
        # Convertir valores que no son serializables
        if hasattr(value, 'isoformat'):  # DateTime, Date
            value = value.isoformat()
        elif hasattr(value, '__dict__'):  # Objetos relacionados
            value = str(value)
        data[field.name] = value
    return data


@receiver(post_save, sender=User)
def audit_user_create_update(sender, instance, created, **kwargs):
    """Registrar creación o actualización de usuarios"""
    try:
        from .models_audit import AuditLog
        
        # Solo registrar si el request está disponible (evitar errores en tests/migrations)
        # Esto se puede mejorar con thread-local storage si es necesario
        
        if created:
            accion = 'CREATE'
            descripcion = f'Usuario "{instance.username}" creado'
            datos_nuevos = serialize_model(instance)
            datos_anteriores = None
        else:
            accion = 'UPDATE'
            descripcion = f'Usuario "{instance.username}" actualizado'
            # En post_save no tenemos acceso a datos anteriores fácilmente
            # Se puede mejorar usando pre_save
            datos_nuevos = serialize_model(instance)
            datos_anteriores = None
        
        # Obtener request del contexto si está disponible
        # Por ahora, creamos el registro sin request (usuario será None si no está autenticado)
        # En producción, se puede usar thread-local storage para pasar el request
        AuditLog.objects.create(
            usuario=None,  # Se puede mejorar con thread-local
            accion=accion,
            modelo='User',
            content_type=None,  # Se puede obtener del modelo
            object_id=instance.pk,
            descripcion=descripcion,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos
        )
    except Exception:
        # No fallar si hay error en auditoría
        pass


@receiver(post_save, sender=Product)
def audit_product_create_update(sender, instance, created, **kwargs):
    """Registrar creación o actualización de productos"""
    try:
        from .models_audit import AuditLog
        from django.contrib.contenttypes.models import ContentType
        
        if created:
            accion = 'CREATE'
            descripcion = f'Producto "{instance.name}" (SKU: {instance.sku}) creado'
        else:
            accion = 'UPDATE'
            descripcion = f'Producto "{instance.name}" (SKU: {instance.sku}) actualizado'
        
        content_type = ContentType.objects.get_for_model(Product)
        AuditLog.objects.create(
            usuario=instance.creado_por if hasattr(instance, 'creado_por') else None,
            accion=accion,
            modelo='Product',
            content_type=content_type,
            object_id=instance.pk,
            descripcion=descripcion
        )
    except Exception:
        pass


@receiver(post_delete, sender=Product)
def audit_product_delete(sender, instance, **kwargs):
    """Registrar eliminación de productos"""
    try:
        from .models_audit import AuditLog
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(Product)
        datos_anteriores = serialize_model(instance)
        
        AuditLog.objects.create(
            usuario=None,  # En delete no tenemos fácil acceso al usuario
            accion='DELETE',
            modelo='Product',
            content_type=content_type,
            object_id=instance.pk,
            descripcion=f'Producto "{instance.name}" (SKU: {instance.sku}) eliminado',
            datos_anteriores=datos_anteriores
        )
    except Exception:
        pass


@receiver(post_save, sender=Proveedor)
def audit_proveedor_create_update(sender, instance, created, **kwargs):
    """Registrar creación o actualización de proveedores"""
    try:
        from .models_audit import AuditLog
        from django.contrib.contenttypes.models import ContentType
        
        if created:
            accion = 'CREATE'
            descripcion = f'Proveedor "{instance.razon_social}" (RUT: {instance.rut}) creado'
        else:
            accion = 'UPDATE'
            descripcion = f'Proveedor "{instance.razon_social}" (RUT: {instance.rut}) actualizado'
        
        content_type = ContentType.objects.get_for_model(Proveedor)
        AuditLog.objects.create(
            usuario=None,
            accion=accion,
            modelo='Proveedor',
            content_type=content_type,
            object_id=instance.pk,
            descripcion=descripcion
        )
    except Exception:
        pass


@receiver(post_save, sender=MovimientoInventario)
def audit_movimiento_create(sender, instance, created, **kwargs):
    """Registrar creación de movimientos de inventario"""
    try:
        from .models_audit import AuditLog
        from django.contrib.contenttypes.models import ContentType
        
        if created:
            content_type = ContentType.objects.get_for_model(MovimientoInventario)
            AuditLog.objects.create(
                usuario=instance.creado_por if instance.creado_por else None,
                accion='CREATE',
                modelo='MovimientoInventario',
                content_type=content_type,
                object_id=instance.pk,
                descripcion=f'Movimiento de inventario: {instance.get_tipo_display()} - {instance.producto.sku} - Cantidad: {instance.cantidad}'
            )
    except Exception:
        pass
