"""
Modelo de auditoría para eventos críticos del sistema
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class AuditLog(models.Model):
    """Modelo para registrar eventos críticos del sistema"""
    
    ACCION_CHOICES = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
        ('LOGIN', 'Iniciar Sesión'),
        ('LOGOUT', 'Cerrar Sesión'),
        ('PASSWORD_RESET', 'Resetear Contraseña'),
        ('PASSWORD_CHANGE', 'Cambiar Contraseña'),
        ('APPROVE', 'Aprobar'),
        ('REJECT', 'Rechazar'),
        ('EXPORT', 'Exportar'),
        ('IMPORT', 'Importar'),
    ]
    
    # Información del evento
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='Usuario'
    )
    fecha_hora = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha y Hora'
    )
    accion = models.CharField(
        max_length=50,
        choices=ACCION_CHOICES,
        verbose_name='Acción'
    )
    modelo = models.CharField(
        max_length=100,
        verbose_name='Modelo',
        help_text='Nombre del modelo afectado (ej: Product, User, Proveedor)'
    )
    
    # Referencia genérica al objeto afectado
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Tipo de Contenido'
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    objeto = GenericForeignKey('content_type', 'object_id')
    
    # Detalles adicionales
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Detalles adicionales del evento'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Dirección IP'
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent',
        help_text='Información del navegador/cliente'
    )
    cambios = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Cambios',
        help_text='Detalles de los cambios realizados (JSON)'
    )
    
    # Información del objeto antes/después (para UPDATE y DELETE)
    datos_anteriores = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Datos Anteriores',
        help_text='Estado anterior del objeto (JSON)'
    )
    datos_nuevos = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Datos Nuevos',
        help_text='Estado nuevo del objeto (JSON)'
    )
    
    class Meta:
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['-fecha_hora'], name='audit_fecha_idx'),
            models.Index(fields=['usuario', '-fecha_hora'], name='audit_usuario_fecha_idx'),
            models.Index(fields=['modelo', '-fecha_hora'], name='audit_modelo_fecha_idx'),
            models.Index(fields=['accion', '-fecha_hora'], name='audit_accion_fecha_idx'),
        ]
    
    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else 'Anónimo'
        return f"{self.fecha_hora.strftime('%Y-%m-%d %H:%M')} - {usuario_str} - {self.get_accion_display()} - {self.modelo}"
    
    @classmethod
    def registrar(cls, request, accion, modelo, objeto=None, descripcion='', cambios=None, datos_anteriores=None, datos_nuevos=None):
        """
        Método helper para registrar eventos de auditoría
        
        Args:
            request: Objeto HttpRequest (para obtener usuario, IP, user agent)
            accion: Acción realizada (debe estar en ACCION_CHOICES)
            modelo: Nombre del modelo afectado (ej: 'Product', 'User')
            objeto: Instancia del objeto afectado (opcional)
            descripcion: Descripción adicional del evento
            cambios: Diccionario con los cambios realizados
            datos_anteriores: Estado anterior del objeto (para UPDATE/DELETE)
            datos_nuevos: Estado nuevo del objeto (para UPDATE/CREATE)
        """
        usuario = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        
        # Obtener ContentType si se proporciona objeto
        content_type = None
        object_id = None
        if objeto:
            content_type = ContentType.objects.get_for_model(objeto)
            object_id = objeto.pk
        
        # Obtener IP y User Agent
        ip_address = None
        user_agent = ''
        if request:
            # Intentar obtener IP real (considerando proxies)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limitar tamaño
        
        return cls.objects.create(
            usuario=usuario,
            accion=accion,
            modelo=modelo,
            content_type=content_type,
            object_id=object_id,
            descripcion=descripcion,
            ip_address=ip_address,
            user_agent=user_agent,
            cambios=cambios,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos
        )
