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
    
    # Intentar cargar el archivo principal primero
    result = False
    if os.path.exists(fixtures_file):
        print_info(f"Archivo de fixtures encontrado: {fixtures_file}")
        print_info("Intentando cargar datos iniciales...")
        result = run_command(
            f"{sys.executable} manage.py loaddata {fixtures_file}",
            "Carga de datos iniciales"
        )
        
        # Si falla por encoding, intentar con fixtures individuales
        if not result:
            print_error("Error al cargar datos_iniciales.json (posible problema de encoding)")
            print_info("Intentando cargar fixtures individuales como alternativa...")
            result = False  # Continuar con fixtures individuales
        else:
            print_success("Datos iniciales cargados correctamente")
    
    # Si el archivo principal no existe o falló, usar fixtures individuales
    if not result:
        if not os.path.exists(fixtures_file):
            print_info(f"No se encontró el archivo: {fixtures_file}")
        print_info("Cargando fixtures individuales...")
        
        # Cargar fixtures existentes uno por uno en orden correcto
        fixtures = [
            "fixtures/03_organizacion_zona_dispositivo_es.json",  # Primero organizaciones
            "fixtures/00_catalogo_categoria_producto_es.json",   # Luego categorías y productos
            "fixtures/01_catalogo_alertas_es.json",               # Después alertas
            "fixtures/02_catalogo_producto_alert_es.json",        # Relaciones producto-alerta
            "fixtures/04_mediciones_ejemplo_es.json",              # Por último mediciones
        ]
        
        result = True
        for fixture in fixtures:
            if os.path.exists(fixture):
                if not run_command(
                    f"{sys.executable} manage.py loaddata {fixture}",
                    f"Cargando {os.path.basename(fixture)}"
                ):
                    result = False
            else:
                print_info(f"Fixture no encontrado (opcional): {fixture}")
    
    # Verificar que los productos se cargaron correctamente y aprobarlos si es necesario
    if result:
        try:
            import django
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulceria.settings')
            django.setup()
            from production.models import Product
            from django.contrib.auth.models import User
            from django.utils import timezone
            
            product_count = Product.objects.count()
            if product_count > 0:
                print_success(f"Productos cargados: {product_count}")
                
                # Aprobar automáticamente los productos iniciales que estén pendientes
                productos_pendientes = Product.objects.filter(estado_aprobacion='PENDIENTE')
                if productos_pendientes.exists():
                    # Obtener el usuario admin para aprobar
                    try:
                        admin_user = User.objects.filter(is_superuser=True).first()
                        if admin_user:
                            productos_pendientes.update(
                                estado_aprobacion='APROBADO',
                                aprobado_por=admin_user,
                                fecha_aprobacion=timezone.now()
                            )
                            print_success(f"Productos aprobados automáticamente: {productos_pendientes.count()}")
                        else:
                            print_info("No se encontró usuario admin para aprobar productos")
                    except Exception as e:
                        print_info(f"No se pudieron aprobar productos automáticamente: {str(e)}")
            else:
                print_error("No se cargaron productos")
                result = False
        except Exception as e:
            print_error(f"Error al verificar productos: {str(e)}")
    
    return result

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

def create_categories():
    """Crear categorías de dulces"""
    print_step(4.5, "Creando Categorías de Dulces")
    
    result = run_command(
        f"{sys.executable} manage.py create_categorias_dulces",
        "Creación de categorías de dulces"
    )
    
    return result

def generate_test_data(proveedores=5000, productos=10000, movimientos=10000):
    """Generar datos de prueba para stress test"""
    print_step(5, f"Generando Datos de Prueba ({proveedores} proveedores, {productos} productos, {movimientos} movimientos)")
    
    print_info("⏳ Este proceso puede tardar varios minutos...")
    print_info("   Por favor, sé paciente. No interrumpas el proceso.")
    
    result = run_command(
        f"{sys.executable} manage.py generate_test_data --proveedores {proveedores} --productos {productos} --movimientos {movimientos}",
        f"Generación de datos de prueba ({proveedores} proveedores, {productos} productos, {movimientos} movimientos)"
    )
    
    if result:
        print_success("Datos de prueba generados correctamente")
        print("\n📋 Datos generados:")
        print(f"   • {proveedores} proveedores")
        print(f"   • {productos} productos")
        print(f"   • {movimientos} movimientos de inventario")
        print("\n💡 Los proveedores son buscables por RUT, razón social y email")
    
    return result

def collect_static():
    """Recolectar archivos estáticos"""
    print_step(6, "Recolectando Archivos Estáticos")
    
    # Verificar que STATICFILES_DIRS esté configurado
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulceria.settings')
        django.setup()
        from django.conf import settings
        
        if not hasattr(settings, 'STATICFILES_DIRS') or not settings.STATICFILES_DIRS:
            print_error("STATICFILES_DIRS no está configurado en settings.py")
            print_info("Agrega: STATICFILES_DIRS = [BASE_DIR / 'static']")
            return False
        else:
            print_info(f"STATICFILES_DIRS configurado: {settings.STATICFILES_DIRS}")
    except Exception as e:
        print_info(f"No se pudo verificar STATICFILES_DIRS: {str(e)}")
    
    # Recolectar archivos estáticos (necesario en producción)
    result = run_command(
        f"{sys.executable} manage.py collectstatic --noinput --clear",
        "Recolección de archivos estáticos"
    )
    
    if result:
        print_success("Archivos estáticos recolectados correctamente")
    else:
        print_info("Advertencia: No se pudieron recolectar archivos estáticos")
        print_info("Esto puede ser normal si no hay archivos estáticos personalizados")
    
    return True  # No es crítico, continuar aunque falle

def verify_static_files():
    """Verificar archivos estáticos y logos"""
    print_info("\nVerificando archivos estáticos y logos...")
    
    try:
        from django.conf import settings
        
        # Verificar STATIC_ROOT
        static_root = settings.STATIC_ROOT
        static_root_exists = os.path.exists(static_root)
        
        if static_root_exists:
            print_success(f"STATIC_ROOT existe: {static_root}")
        else:
            print_error(f"STATIC_ROOT no existe: {static_root}")
            print_info("Ejecuta: python manage.py collectstatic")
            return False
        
        # Verificar logos en static/img
        static_img_dir = os.path.join(settings.BASE_DIR, 'static', 'img')
        staticfiles_img_dir = os.path.join(static_root, 'img')
        
        logos_esperados = [
            'LOGO-Lilis-rojo.png',
            'Logo-lilis-dorado.png',
            'lilis_productos.png'
        ]
        
        logos_ok = 0
        logos_faltantes = []
        
        for logo in logos_esperados:
            # Verificar en static/img (origen)
            ruta_static = os.path.join(static_img_dir, logo)
            existe_static = os.path.exists(ruta_static)
            
            # Verificar en staticfiles/img (destino después de collectstatic)
            ruta_staticfiles = os.path.join(staticfiles_img_dir, logo)
            existe_staticfiles = os.path.exists(ruta_staticfiles) if os.path.exists(staticfiles_img_dir) else False
            
            if existe_staticfiles:
                logos_ok += 1
                print_success(f"Logo '{logo}' encontrado en staticfiles")
            elif existe_static:
                logos_faltantes.append(logo)
                print_info(f"⚠️  Logo '{logo}' existe en static pero no en staticfiles")
            else:
                logos_faltantes.append(logo)
                print_error(f"Logo '{logo}' no encontrado")
        
        if logos_faltantes:
            print_info(f"\n⚠️  {len(logos_faltantes)} logos faltantes en staticfiles")
            print_info("Ejecuta: python manage.py collectstatic --noinput")
            return False
        else:
            print_success(f"Todos los logos están disponibles ({logos_ok}/{len(logos_esperados)})")
            return True
            
    except Exception as e:
        print_error(f"Error al verificar archivos estáticos: {str(e)}")
        return False

def verify_product_images():
    """Verificar imágenes de productos"""
    print_info("\nVerificando imágenes de productos...")
    
    try:
        from production.models import Product
        from django.conf import settings
        
        products = Product.objects.all()
        products_count = products.count()
        
        if products_count == 0:
            print_info("No hay productos para verificar")
            return True
        
        products_with_images = 0
        products_without_images = 0
        products_with_file = 0
        products_without_file = 0
        
        for product in products:
            if product.imagen and product.imagen.name:
                products_with_images += 1
                
                # Verificar si el archivo existe físicamente
                try:
                    if hasattr(product.imagen, 'path'):
                        ruta_fisica = product.imagen.path
                        if os.path.exists(ruta_fisica):
                            products_with_file += 1
                        else:
                            products_without_file += 1
                            print_info(f"⚠️  Imagen no encontrada para '{product.name}': {ruta_fisica}")
                except Exception as e:
                    products_without_file += 1
                    print_info(f"⚠️  Error al verificar imagen de '{product.name}': {str(e)}")
            else:
                products_without_images += 1
        
        print_info(f"Productos con imágenes en BD: {products_with_images}")
        print_info(f"Productos sin imágenes: {products_without_images}")
        
        if products_with_file > 0:
            print_success(f"Imágenes físicas encontradas: {products_with_file}")
        
        if products_without_file > 0:
            print_info(f"⚠️  Imágenes físicas faltantes: {products_without_file}")
            print_info("(Esto es normal en AWS si usas S3, o si las imágenes no se han subido)")
        
        return True
        
    except Exception as e:
        print_error(f"Error al verificar imágenes de productos: {str(e)}")
        return False

def verify_installation():
    """Verificar que todo esté correcto"""
    print_step(7, "Verificando Instalación")
    
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
        
        # Verificar productos
        if products == 0:
            print_error("No hay productos cargados")
            return False
        
        # Verificar archivos estáticos y logos
        static_ok = verify_static_files()
        
        # Verificar imágenes de productos
        images_ok = verify_product_images()
        
        # La verificación es exitosa si hay productos y los usuarios tienen perfiles
        # Los logos e imágenes son advertencias, no errores críticos
        return True
        
    except Exception as e:
        print_error(f"Error en la verificación: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def ask_yes_no(question, default=False):
    """Preguntar al usuario sí/no"""
    default_text = "S/n" if not default else "s/N"
    response = input(f"{question} ({default_text}): ").strip().lower()
    
    if response == '':
        return default
    return response in ['s', 'si', 'sí', 'y', 'yes']

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
    
    # Verificar si se debe generar datos de prueba
    generate_data = False
    proveedores = 5000
    productos = 10000
    movimientos = 10000
    
    # Verificar variable de entorno primero
    if os.getenv("GENERATE_TEST_DATA", "").lower() in ["true", "1", "yes", "si"]:
        generate_data = True
        print_info("Variable de entorno GENERATE_TEST_DATA detectada - Se generarán datos de prueba")
    else:
        # Preguntar al usuario
        print("\n" + "="*70)
        print("  ¿Deseas generar datos de prueba para stress test?")
        print("="*70)
        print("\nEsto creará:")
        print(f"   • {proveedores} proveedores")
        print(f"   • {productos} productos")
        print(f"   • {movimientos} movimientos de inventario")
        print("\n⏳ Tiempo estimado: 5-15 minutos")
        print("⚠️  Solo necesario si quieres probar con grandes volúmenes de datos\n")
        
        generate_data = ask_yes_no("¿Generar datos de prueba?", default=False)
    
    # Ejecutar pasos de configuración
    steps = [
        ("Verificar Base de Datos", check_database_config),
        ("Aplicar Migraciones", apply_migrations),
        ("Cargar Datos Iniciales", load_initial_data),
        ("Crear Usuarios", create_test_users),
        ("Crear Categorías", create_categories),
    ]
    
    # Agregar generación de datos si se solicita
    if generate_data:
        steps.append(
            ("Generar Datos de Prueba", lambda: generate_test_data(proveedores, productos, movimientos))
        )
    
    # Agregar pasos finales
    steps.extend([
        ("Recolectar Estáticos", collect_static),
        ("Verificar Instalación", verify_installation),
    ])
    
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

