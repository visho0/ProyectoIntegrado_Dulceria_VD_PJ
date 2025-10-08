#!/usr/bin/env python
"""
Script de verificación de configuración para el proyecto Dulcería
Ejecutar: python verificar_configuracion.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulceria.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from organizations.models import Organization
from django.db import connection

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def check_database_connection():
    """Verificar conexión a la base de datos"""
    print_header("1. Verificando Conexión a la Base de Datos")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print_success("Conexión a MySQL exitosa")
                return True
    except Exception as e:
        print_error(f"Error al conectar con MySQL: {str(e)}")
        print_warning("Verifica que WAMP esté corriendo y las credenciales sean correctas")
        return False

def check_tables():
    """Verificar que las tablas existan"""
    print_header("2. Verificando Tablas de la Base de Datos")
    try:
        tables = connection.introspection.table_names()
        required_tables = [
            'auth_user',
            'accounts_userprofile',
            'organizations_organization',
            'production_product',
            'production_category',
        ]
        
        all_exist = True
        for table in required_tables:
            if table in tables:
                print_success(f"Tabla '{table}' existe")
            else:
                print_error(f"Tabla '{table}' NO existe")
                all_exist = False
        
        if not all_exist:
            print_warning("Ejecuta: python manage.py migrate")
        
        return all_exist
    except Exception as e:
        print_error(f"Error al verificar tablas: {str(e)}")
        return False

def check_organizations():
    """Verificar que existan organizaciones"""
    print_header("3. Verificando Organizaciones")
    try:
        org_count = Organization.objects.count()
        if org_count > 0:
            print_success(f"Se encontraron {org_count} organizaciones")
            for org in Organization.objects.all():
                print(f"   - {org.name}")
            return True
        else:
            print_error("No hay organizaciones creadas")
            print_warning("Ejecuta: python manage.py create_test_users")
            return False
    except Exception as e:
        print_error(f"Error al verificar organizaciones: {str(e)}")
        return False

def check_users():
    """Verificar que existan usuarios"""
    print_header("4. Verificando Usuarios")
    try:
        user_count = User.objects.count()
        if user_count > 0:
            print_success(f"Se encontraron {user_count} usuarios")
            
            # Verificar superusuarios
            superusers = User.objects.filter(is_superuser=True)
            if superusers.exists():
                print_success(f"Superusuarios encontrados: {', '.join([u.username for u in superusers])}")
            else:
                print_warning("No hay superusuarios creados")
            
            return True
        else:
            print_error("No hay usuarios creados")
            print_warning("Ejecuta: python manage.py create_test_users")
            return False
    except Exception as e:
        print_error(f"Error al verificar usuarios: {str(e)}")
        return False

def check_user_profiles():
    """Verificar que los usuarios tengan perfiles"""
    print_header("5. Verificando Perfiles de Usuario")
    try:
        users = User.objects.all()
        users_without_profile = []
        users_with_profile = []
        
        for user in users:
            try:
                profile = user.userprofile
                users_with_profile.append(user)
                print_success(f"Usuario '{user.username}' tiene perfil (Rol: {profile.get_role_display()}, Org: {profile.organization.name})")
            except UserProfile.DoesNotExist:
                users_without_profile.append(user)
                print_error(f"Usuario '{user.username}' NO tiene perfil")
        
        if users_without_profile:
            print_warning("Algunos usuarios no tienen perfil. Ejecútalos:")
            print_warning("  python manage.py create_test_users")
            print_warning("  O crea los perfiles manualmente desde /admin/")
            return False
        elif len(users_with_profile) > 0:
            print_success("Todos los usuarios tienen perfiles")
            return True
        else:
            print_error("No hay usuarios creados")
            return False
            
    except Exception as e:
        print_error(f"Error al verificar perfiles: {str(e)}")
        return False

def check_test_users():
    """Verificar usuarios de prueba específicos"""
    print_header("6. Verificando Usuarios de Prueba")
    test_users = ['admin', 'gerente', 'empleado']
    found = []
    missing = []
    
    for username in test_users:
        try:
            user = User.objects.get(username=username)
            if hasattr(user, 'userprofile'):
                found.append(username)
                print_success(f"Usuario de prueba '{username}' existe y tiene perfil")
            else:
                print_warning(f"Usuario '{username}' existe pero NO tiene perfil")
                missing.append(username)
        except User.DoesNotExist:
            missing.append(username)
            print_warning(f"Usuario de prueba '{username}' NO existe")
    
    if missing:
        print_warning("Ejecuta para crear usuarios de prueba: python manage.py create_test_users")
        return False
    
    return len(found) == len(test_users)

def check_media_files():
    """Verificar configuración de archivos media"""
    print_header("7. Verificando Configuración de Media Files")
    from django.conf import settings
    
    if hasattr(settings, 'MEDIA_ROOT'):
        media_root = settings.MEDIA_ROOT
        if os.path.exists(media_root):
            print_success(f"Carpeta MEDIA_ROOT existe: {media_root}")
        else:
            print_warning(f"Carpeta MEDIA_ROOT no existe: {media_root}")
            print_warning("Se creará automáticamente al subir archivos")
        return True
    else:
        print_error("MEDIA_ROOT no está configurado en settings.py")
        return False

def main():
    print_header("🍬 VERIFICACIÓN DE CONFIGURACIÓN - PROYECTO DULCERÍA")
    print("Este script verificará que tu entorno esté configurado correctamente\n")
    
    results = []
    
    # Ejecutar todas las verificaciones
    results.append(("Conexión DB", check_database_connection()))
    results.append(("Tablas", check_tables()))
    results.append(("Organizaciones", check_organizations()))
    results.append(("Usuarios", check_users()))
    results.append(("Perfiles", check_user_profiles()))
    results.append(("Usuarios Prueba", check_test_users()))
    results.append(("Media Files", check_media_files()))
    
    # Resumen
    print_header("📊 RESUMEN DE VERIFICACIÓN")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{'='*60}")
    print(f"  Resultado: {passed}/{total} verificaciones pasadas")
    print(f"{'='*60}")
    
    if passed == total:
        print_success("\n🎉 ¡Todo está configurado correctamente!")
        print("Puedes ejecutar: python manage.py runserver")
    else:
        print_error("\n⚠️  Hay problemas en la configuración")
        print("\nPasos sugeridos:")
        print("1. python manage.py migrate")
        print("2. python manage.py create_test_users")
        print("3. python verificar_configuracion.py (ejecutar de nuevo)")
        print("\nSi los problemas persisten, revisa GUIA_CONFIGURACION_COMPAÑERO.md")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print_error(f"\nError crítico al ejecutar la verificación: {str(e)}")
        print("\nAsegúrate de:")
        print("1. Estar en el directorio 'dulceria/'")
        print("2. Tener el entorno virtual activado")
        print("3. Haber instalado todas las dependencias: pip install -r requirements.txt")
        sys.exit(1)

