"""
Script de prueba para verificar el envío de correos electrónicos
Ejecutar con: python manage.py shell < manage_commands/test_email.py
O mejor: python manage.py shell
>>> exec(open('manage_commands/test_email.py').read())
"""
from django.core.mail import send_mail
from django.conf import settings
import sys

def test_email_sending():
    """Prueba el envío de un correo de prueba"""
    print("=" * 60)
    print("PRUEBA DE ENVÍO DE CORREO ELECTRÓNICO")
    print("=" * 60)
    
    # Verificar configuración
    print(f"\n📧 Configuración de Email:")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"   EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NO CONFIGURADA'}")
    
    # Solicitar email de destino
    print("\n" + "=" * 60)
    recipient_email = input("Ingresa el email de destino para la prueba: ").strip()
    
    if not recipient_email:
        print("❌ Error: Debes ingresar un email de destino")
        return False
    
    # Crear mensaje de prueba
    subject = f'[PRUEBA] Email desde {settings.SITE_NAME}'
    message = f"""
Este es un correo de prueba desde {settings.SITE_NAME}.

Si recibes este correo, significa que la configuración de Gmail SMTP está funcionando correctamente.

Configuración:
- Backend: {settings.EMAIL_BACKEND}
- Host: {settings.EMAIL_HOST}
- Puerto: {settings.EMAIL_PORT}
- TLS: {settings.EMAIL_USE_TLS}

¡La configuración de email está lista para usar!
"""
    
    try:
        print(f"\n📤 Enviando correo a {recipient_email}...")
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        
        if result:
            print("✅ ¡Correo enviado exitosamente!")
            print(f"   Revisa la bandeja de entrada (y spam) de {recipient_email}")
            return True
        else:
            print("❌ Error: No se pudo enviar el correo")
            return False
            
    except Exception as e:
        print(f"❌ Error al enviar correo: {str(e)}")
        print(f"\n🔍 Posibles causas:")
        print("   1. Credenciales incorrectas (email o contraseña de aplicación)")
        print("   2. Verificación en 2 pasos no habilitada en Gmail")
        print("   3. Contraseña de aplicación inválida o expirada")
        print("   4. Firewall bloqueando el puerto 587")
        print("   5. EMAIL_HOST_USER no configurado correctamente en .env")
        return False

if __name__ == '__main__':
    # Si se ejecuta directamente desde shell
    test_email_sending()
