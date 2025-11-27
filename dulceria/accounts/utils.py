"""
Utilidades para gestión de usuarios y contraseñas
"""
import secrets
import string
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def generate_temporary_password(length=12):
    """
    Genera una contraseña provisoria robusta.
    Requisitos:
    - Longitud mínima: 8 caracteres
    - Al menos 1 mayúscula, 1 minúscula, 1 dígito y 1 carácter especial
    """
    if length < 8:
        length = 12
    
    # Caracteres permitidos
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Asegurar al menos un carácter de cada tipo
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(special),
    ]
    
    # Completar con caracteres aleatorios
    all_chars = uppercase + lowercase + digits + special
    password.extend(secrets.choice(all_chars) for _ in range(length - 4))
    
    # Mezclar aleatoriamente
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)


def send_temporary_password_email(user, temporary_password, request=None):
    """
    Envía un correo con la contraseña provisoria al usuario.
    """
    try:
        # Obtener URL base
        if request:
            base_url = f"{request.scheme}://{request.get_host()}"
        else:
            base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        
        login_url = f"{base_url}/login/"
        
        # Renderizar template de email
        context = {
            'user': user,
            'username': user.username,
            'temporary_password': temporary_password,
            'login_url': login_url,
            'site_name': getattr(settings, 'SITE_NAME', 'Sistema de Gestión'),
        }
        
        html_message = render_to_string('accounts/temporary_password_email.html', context)
        plain_message = strip_tags(html_message)
        
        subject = f'Bienvenido a {context["site_name"]} - Credenciales de acceso'
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")
        return False


def send_password_reset_email(user, temporary_password, request=None):
    """
    Envía un correo con nueva contraseña temporal después de un reset por administrador.
    """
    try:
        # Obtener URL base
        if request:
            base_url = f"{request.scheme}://{request.get_host()}"
        else:
            base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        
        login_url = f"{base_url}/login/"
        
        # Renderizar template de email
        context = {
            'user': user,
            'username': user.username,
            'temporary_password': temporary_password,
            'login_url': login_url,
            'site_name': getattr(settings, 'SITE_NAME', 'Sistema de Gestión'),
        }
        
        html_message = render_to_string('accounts/password_reset_admin_email.html', context)
        plain_message = strip_tags(html_message)
        
        subject = f'{context["site_name"]} - Nueva contraseña temporal'
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")
        return False

