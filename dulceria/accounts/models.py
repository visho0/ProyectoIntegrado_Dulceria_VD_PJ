from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def validate_rut_chileno(value):
    """Validador de RUT chileno"""
    if not value:
        return
    
    # Eliminar puntos y guión
    rut = value.replace('.', '').replace('-', '')
    
    if len(rut) < 8 or len(rut) > 9:
        raise ValidationError('El RUT debe tener entre 8 y 9 caracteres')
    
    # Separar cuerpo y dígito verificador
    cuerpo = rut[:-1]
    dv = rut[-1].upper()
    
    # Validar que el cuerpo sea numérico
    if not cuerpo.isdigit():
        raise ValidationError('El RUT solo debe contener números (excepto el dígito verificador)')
    
    # Validar que el DV sea K o número
    if dv not in '0123456789K':
        raise ValidationError('El dígito verificador debe ser un número o K')
    
    # Calcular DV correcto
    suma = 0
    multiplo = 2
    
    for r in reversed(cuerpo):
        suma += int(r) * multiplo
        multiplo += 1
        if multiplo > 7:
            multiplo = 2
    
    resto = suma % 11
    dv_calculado = str(11 - resto) if resto != 0 else '0'
    
    # Convertir 11 a K
    if dv_calculado == '10':
        dv_calculado = 'K'
    
    if dv != dv_calculado:
        raise ValidationError(f'El RUT no es válido. El dígito verificador correcto es {dv_calculado}')


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('employee', 'Empleado'),
        ('viewer', 'Visualizador'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='employee', verbose_name='Rol')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    organization = models.ForeignKey('organizations.Organization', on_delete=models.PROTECT, verbose_name='Organización')

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class Cliente(models.Model):
    """Modelo para clientes externos de la dulcería"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario')
    rut = models.CharField(max_length=12, validators=[validate_rut_chileno], verbose_name='RUT', help_text='Formato: 12345678-9')
    first_name = models.CharField(max_length=150, verbose_name='Nombre')
    last_name = models.CharField(max_length=150, verbose_name='Apellido')
    email = models.EmailField(verbose_name='Correo Electrónico')
    phone = models.CharField(max_length=20, verbose_name='Teléfono')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.rut})"