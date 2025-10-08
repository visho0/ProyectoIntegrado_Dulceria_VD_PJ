#!/usr/bin/env python
"""
Script de Configuración Automática - Proyecto Dulcería
Ejecutar: python configurar_proyecto.py

Este script configura automáticamente el proyecto para que se vea
exactamente igual en cualquier computadora.
"""

import os
import sys
import subprocess

def print_header(text):
    print("\n" + "="*70)
    print(f"  🍬 {text}")
    print("="*70)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def print_step(number, text):
    print(f"\n{'='*70}")
    print(f"  PASO {number}: {text}")
    print(f"{'='*70}")

def run_command(cmd, description):
    """Ejecutar un comando y mostrar el resultado"""
    print_info(f"Ejecutando: {description}...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            print_success(f"{description} - Completado")
            if result.stdout and result.stdout.strip():
                print(result.stdout)
            return True
        else:
            print_error(f"{description} - Error")
            if result.stderr:
                print(result.stderr)
            return False
            
    except Exception as e:
        print_error(f"Error al ejecutar {description}: {str(e)}")
        return False

def check_database_config():
    """Verificar configuración de base de datos"""
    print_step(1, "Verificando Configuración de Base de Datos")
    
    try:
        # Importar settings
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulceria.settings')
        django.setup()
        
        from django.conf import settings
        
        db_config = settings.DATABASES['default']
        print_info(f"Motor de BD: {db_config['ENGINE']}")
        print_info(f"Nombre BD: {db_config['NAME']}")
        print_info(f"Host: {db_config.get('HOST', 'localhost')}")
        
        # Verificar conexión
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print_success("Conexión a la base de datos exitosa")
                return True
                
    except Exception as e:
        print_error(f"Error en la configuración de BD: {str(e)}")
        print("\n⚠️  INSTRUCCIONES:")
        print("1. Asegúrate de que MySQL esté corriendo (WAMP)")
        print("2. Crea una base de datos llamada 'dulceria_db' en phpMyAdmin")
        print("3. Verifica que settings.py tenga la configuración correcta")
        return False

def apply_migrations():
    """Aplicar migraciones"""
    print_step(2, "Aplicando Migraciones")
    return run_command(
        f"{sys.executable} manage.py migrate",
        "Migraciones de base de datos"
    )

def load_initial_data():
    """Cargar datos iniciales desde fixtures"""
    print_step(3, "Cargando Datos Iniciales")
    
    # Verificar si existe el archivo de fixtures
    fixtures_file = "fixtures/datos_iniciales.json"
    
    if os.path.exists(fixtures_file):
        print_info(f"Archivo de fixtures encontrado: {fixtures_file}")
        return run_command(
            f"{sys.executable} manage.py loaddata {fixtures_file}",
            "Carga de datos iniciales"
        )
    else:
        print_error(f"No se encontró el archivo: {fixtures_file}")
        print_info("Intentando cargar fixtures individuales...")
        
        # Cargar fixtures existentes uno por uno
        fixtures = [
            "fixtures/00_catalogo_categoria_producto_es.json",
            "fixtures/01_catalogo_alertas_es.json",
            "fixtures/02_catalogo_producto_alert_es.json",
            "fixtures/03_organizacion_zona_dispositivo_es.json",
            "fixtures/04_mediciones_ejemplo_es.json",
        ]
        
        success = True
        for fixture in fixtures:
            if os.path.exists(fixture):
                if not run_command(
                    f"{sys.executable} manage.py loaddata {fixture}",
                    f"Cargando {os.path.basename(fixture)}"
                ):
                    success = False
        
        return success

def create_test_users():
    """Crear usuarios de prueba"""
    print_step(4, "Creando Usuarios de Prueba")
    
    result = run_command(
        f"{sys.executable} manage.py create_test_users",
        "Creación de usuarios de prueba"
    )
    
    if result:
        print("\n📋 Usuarios creados:")
        print("   • admin / admin123 (Administrador)")
        print("   • gerente / gerente123 (Gerente)")
        print("   • empleado / empleado123 (Empleado)")
    
    return result

def collect_static():
    """Recolectar archivos estáticos (opcional)"""
    print_step(5, "Recolectando Archivos Estáticos")
    
    # Solo en producción, en desarrollo no es necesario
    print_info("Omitiendo en modo desarrollo")
    return True

def verify_installation():
    """Verificar que todo esté correcto"""
    print_step(6, "Verificando Instalación")
    
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulceria.settings')
        django.setup()
        
        from django.contrib.auth.models import User
        from accounts.models import UserProfile
        from organizations.models import Organization
        from production.models import Product, Category
        
        # Contar registros
        orgs = Organization.objects.count()
        users = User.objects.count()
        profiles = UserProfile.objects.count()
        categories = Category.objects.count()
        products = Product.objects.count()
        
        print_success(f"Organizaciones: {orgs}")
        print_success(f"Usuarios: {users}")
        print_success(f"Perfiles de Usuario: {profiles}")
        print_success(f"Categorías: {categories}")
        print_success(f"Productos: {products}")
        
        # Verificar que los usuarios tengan perfiles
        users_without_profile = User.objects.exclude(
            id__in=UserProfile.objects.values_list('user_id', flat=True)
        ).count()
        
        if users_without_profile > 0:
            print_error(f"{users_without_profile} usuarios sin perfil")
            return False
        else:
            print_success("Todos los usuarios tienen perfil")
        
        return True
        
    except Exception as e:
        print_error(f"Error en la verificación: {str(e)}")
        return False

def show_final_instructions():
    """Mostrar instrucciones finales"""
    print_header("¡CONFIGURACIÓN COMPLETADA! 🎉")
    
    print("\n✅ El proyecto está listo para usar en este computador")
    print("\n🚀 Para iniciar el servidor, ejecuta:")
    print("   python manage.py runserver")
    
    print("\n🌐 Luego abre tu navegador en:")
    print("   http://127.0.0.1:8000")
    
    print("\n🔐 Usuarios disponibles:")
    print("   • Admin:    admin / admin123")
    print("   • Gerente:  gerente / gerente123")
    print("   • Empleado: empleado / empleado123")
    
    print("\n📍 URLs importantes:")
    print("   • Login:     http://127.0.0.1:8000/login/")
    print("   • Dashboard: http://127.0.0.1:8000/dashboard/")
    print("   • Productos: http://127.0.0.1:8000/products/")
    print("   • Admin:     http://127.0.0.1:8000/admin/")
    
    print("\n" + "="*70 + "\n")

def main():
    print_header("CONFIGURACIÓN AUTOMÁTICA - PROYECTO DULCERÍA")
    print("\nEste script configurará el proyecto automáticamente.")
    print("Todo se verá exactamente igual que en el computador original.\n")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("manage.py"):
        print_error("Error: Debes ejecutar este script desde el directorio 'dulceria/'")
        print("Ejecuta: cd dulceria")
        sys.exit(1)
    
    # Ejecutar pasos de configuración
    steps = [
        ("Verificar Base de Datos", check_database_config),
        ("Aplicar Migraciones", apply_migrations),
        ("Cargar Datos Iniciales", load_initial_data),
        ("Crear Usuarios", create_test_users),
        ("Recolectar Estáticos", collect_static),
        ("Verificar Instalación", verify_installation),
    ]
    
    results = []
    
    for step_name, step_function in steps:
        result = step_function()
        results.append((step_name, result))
        
        if not result and step_name in ["Verificar Base de Datos", "Aplicar Migraciones"]:
            print_error(f"\n⚠️  Error crítico en: {step_name}")
            print("No se puede continuar con la configuración.")
            sys.exit(1)
    
    # Mostrar resumen
    print_header("RESUMEN DE CONFIGURACIÓN")
    
    for step_name, result in results:
        status = "✅" if result else "⚠️"
        print(f"{status} {step_name}")
    
    # Verificar si todo fue exitoso
    all_success = all(result for _, result in results)
    
    if all_success:
        show_final_instructions()
    else:
        print_error("\n⚠️  Algunos pasos tuvieron advertencias")
        print("El proyecto debería funcionar, pero revisa los mensajes anteriores.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Configuración cancelada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print_error(f"\nError inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

