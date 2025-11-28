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
    Genera una contraseña provisoria robusta y única.
    Requisitos:
    - Longitud mínima: 12 caracteres
    - Al menos 1 mayúscula, 1 minúscula, 1 dígito y 1 carácter especial
    - No sigue patrones triviales (como "Aa1!Aa1!...")
    - Cada llamada genera una contraseña única y aleatoria
    """
    if length < 12:
        length = 12
    
    # Caracteres permitidos (evitando caracteres confusos)
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    # Caracteres especiales seguros (evitando confusión)
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Usar SystemRandom para mayor seguridad criptográfica
    random_gen = secrets.SystemRandom()
    
    # Intentar generar contraseña única hasta 10 veces
    max_attempts = 10
    for attempt in range(max_attempts):
        # Asegurar al menos un carácter de cada tipo en posiciones aleatorias
        password_chars = [None] * length
        
        # Asignar uno de cada tipo en posiciones aleatorias
        required_positions = random_gen.sample(range(length), 4)
        password_chars[required_positions[0]] = secrets.choice(uppercase)
        password_chars[required_positions[1]] = secrets.choice(lowercase)
        password_chars[required_positions[2]] = secrets.choice(digits)
        password_chars[required_positions[3]] = secrets.choice(special)
        
        # Completar el resto con caracteres aleatorios
        all_chars = uppercase + lowercase + digits + special
        for i in range(length):
            if password_chars[i] is None:
                password_chars[i] = secrets.choice(all_chars)
        
        password = ''.join(password_chars)
        
        # Validar que no tenga patrones triviales
        # No debe tener más de 2 caracteres consecutivos iguales
        has_consecutive = any(
            password[i] == password[i+1] == password[i+2]
            for i in range(len(password) - 2)
        )
        
        # No debe tener secuencias obvias (123, abc, ABC, etc.)
        has_sequence = False
        for i in range(len(password) - 2):
            seq = password[i:i+3].lower()
            if seq in ['abc', '123', 'qwe', 'asd', 'zxc']:
                has_sequence = True
                break
        
        # Si no tiene patrones problemáticos, retornar
        if not has_consecutive and not has_sequence:
            return password
    
    # Si después de 10 intentos no encontramos una buena, retornar la última generada
    # (es improbable que todas tengan problemas)
    return password


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

