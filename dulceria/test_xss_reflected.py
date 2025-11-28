"""
Script de prueba para verificar protección contra XSS reflejado
Ejecutar: python manage.py shell < test_xss_reflected.py
"""

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

# Crear cliente de prueba
client = Client()

print("=" * 60)
print("PRUEBA DE PROTECCIÓN CONTRA XSS REFLEJADO")
print("=" * 60)

# Payload de prueba XSS
xss_payload = '<script>alert(1)</script>'

print(f"\n1. Probando payload: {xss_payload}")
print("-" * 60)

# Prueba 1: Formulario de recuperación de contraseña
print("\n[PRUEBA 1] Formulario de Recuperación de Contraseña")
print("URL: /password-reset/")
try:
    response = client.post('/password-reset/', {
        'email': xss_payload
    }, follow=True)
    
    # Verificar que el payload está escapado en la respuesta
    if xss_payload in response.content.decode('utf-8'):
        # Verificar si está escapado (debería aparecer como &lt;script&gt;)
        if '&lt;script&gt;' in response.content.decode('utf-8') or '<script>' not in response.content.decode('utf-8'):
            print("✓ PASS: El payload está correctamente escapado")
            print(f"  El HTML contiene: {response.content.decode('utf-8')[:200]}...")
        else:
            print("✗ FAIL: El payload NO está escapado - VULNERABILIDAD DETECTADA")
    else:
        print("✓ PASS: El payload no aparece en la respuesta (filtrado)")
except Exception as e:
    print(f"✗ ERROR: {str(e)}")

# Prueba 2: Formulario de login
print("\n[PRUEBA 2] Formulario de Login")
print("URL: /accounts/login/")
try:
    response = client.post('/accounts/login/', {
        'username': xss_payload,
        'password': 'test123'
    }, follow=True)
    
    content = response.content.decode('utf-8')
    if '&lt;script&gt;' in content or xss_payload not in content:
        print("✓ PASS: El payload está correctamente escapado")
    else:
        print("✗ FAIL: El payload NO está escapado - VULNERABILIDAD DETECTADA")
        print(f"  Contenido encontrado: {content[:300]}")
except Exception as e:
    print(f"✗ ERROR: {str(e)}")

# Prueba 3: Mensajes flash (messages framework)
print("\n[PRUEBA 3] Sistema de Mensajes Flash")
print("Verificar que los mensajes escapen correctamente")
try:
    from django.contrib import messages
    from django.test import RequestFactory
    
    factory = RequestFactory()
    request = factory.get('/')
    
    # Simular un mensaje con payload XSS
    messages.error(request, f'Error: {xss_payload}')
    
    # Verificar que el mensaje está escapado
    storage = messages.get_messages(request)
    for message in storage:
        message_str = str(message)
        if '&lt;script&gt;' in message_str or '<script>' not in message_str:
            print("✓ PASS: Los mensajes escapan correctamente")
        else:
            print("✗ FAIL: Los mensajes NO escapan - VULNERABILIDAD DETECTADA")
except Exception as e:
    print(f"✗ ERROR: {str(e)}")

print("\n" + "=" * 60)
print("PRUEBA COMPLETADA")
print("=" * 60)
print("\nNOTA: Verifica manualmente en el navegador que:")
print("1. No aparezca un alert() cuando ingresas el payload")
print("2. El texto aparezca como texto plano, no como código HTML")
print("3. En el código fuente HTML, < y > estén escapados como &lt; y &gt;")

