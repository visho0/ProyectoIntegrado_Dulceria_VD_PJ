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
    
    from decimal import Decimal
    from datetime import date, datetime
    
    data = {}
    for field in obj._meta.fields:
        value = getattr(obj, field.name, None)
        
        # Convertir valores que no son serializables a JSON
        if value is None:
            data[field.name] = None
        elif isinstance(value, Decimal):
            # Convertir Decimal a float para JSON
            data[field.name] = float(value)
        elif isinstance(value, (date, datetime)):
            # Convertir fechas a string ISO
            data[field.name] = value.isoformat()
        elif hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool)):
            # Objetos relacionados o complejos
            data[field.name] = str(value)
        else:
            # Valores simples (str, int, float, bool)
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
    from django.db import transaction
    from django.utils import timezone
    from datetime import timedelta
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Capturar TODA la información necesaria ANTES de on_commit
    # En post_delete, el objeto aún existe en memoria pero ya fue eliminado de la BD
    try:
        nombre = getattr(instance, 'name', 'Desconocido')
        sku = getattr(instance, 'sku', 'N/A')
        object_id = instance.pk
        
        # Intentar serializar datos ANTES de on_commit (mientras el objeto existe en memoria)
        try:
            datos_anteriores = serialize_model(instance)
        except Exception as e:
            logger.warning(f'Error al serializar datos del producto eliminado: {str(e)}')
            datos_anteriores = None
    except Exception as e:
        logger.warning(f'Error al obtener información del producto eliminado: {str(e)}')
        nombre = 'Desconocido'
        sku = 'N/A'
        object_id = None
        datos_anteriores = None
    
    # Usar on_commit para ejecutar después de que la transacción se complete
    # Esto evita que errores en auditoría rompan la transacción principal
    def crear_registro_auditoria():
        try:
            from .models_audit import AuditLog
            from django.contrib.contenttypes.models import ContentType
            
            # Verificar si ya existe un registro de auditoría reciente (últimos 5 segundos)
            # Esto evita duplicados cuando la auditoría se registra desde la vista
            content_type = ContentType.objects.get_for_model(Product)
            ahora = timezone.now()
            hace_5_segundos = ahora - timedelta(seconds=5)
            
            registro_existente = AuditLog.objects.filter(
                accion='DELETE',
                modelo='Product',
                content_type=content_type,
                object_id=object_id,
                fecha_hora__gte=hace_5_segundos
            ).exists()
            
            # Solo crear si no existe un registro reciente
            if not registro_existente:
                AuditLog.objects.create(
                    usuario=None,  # En delete no tenemos fácil acceso al usuario desde signal
                    accion='DELETE',
                    modelo='Product',
                    content_type=content_type,
                    object_id=object_id,
                    descripcion=f'Producto "{nombre}" (SKU: {sku}) eliminado',
                    datos_anteriores=datos_anteriores
                )
        except Exception as e:
            # Loggear el error pero no fallar la eliminación
            logger.error(f'Error al registrar auditoría de eliminación de producto: {str(e)}', exc_info=True)
    
    # Ejecutar después de que la transacción se complete
    transaction.on_commit(crear_registro_auditoria)


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
