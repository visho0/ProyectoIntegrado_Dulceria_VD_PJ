#!/usr/bin/env python
"""
Script para exportar datos del proyecto para compartir con compañeros
Ejecutar: python exportar_para_compartir.py
"""

import os
import sys
import subprocess
from datetime import datetime

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def export_fixtures():
    """Exportar datos a fixtures JSON"""
    print_header("📦 Exportando datos a Fixtures JSON")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"fixtures/datos_compartidos_{timestamp}.json"
    
    try:
        # Crear carpeta fixtures si no existe
        os.makedirs("fixtures", exist_ok=True)
        
        print_info("Exportando todos los datos...")
        cmd = [
            sys.executable,
            "manage.py",
            "dumpdata",
            "--indent", "2",
            "--natural-foreign",
            "--natural-primary",
            "--exclude", "contenttypes",
            "--exclude", "auth.permission",
            "--exclude", "sessions.session",
            "--output", output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success(f"Datos exportados a: {output_file}")
            
            # Mostrar tamaño del archivo
            size = os.path.getsize(output_file)
            size_mb = size / (1024 * 1024)
            print_info(f"Tamaño del archivo: {size_mb:.2f} MB")
            
            return output_file
        else:
            print_error(f"Error al exportar: {result.stderr}")
            return None
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def export_mysql_dump():
    """Instrucciones para exportar con mysqldump"""
    print_header("💾 Instrucciones para Exportar con MySQL")
    
    print_info("Hay dos formas de exportar la base de datos MySQL:\n")
    
    print("OPCIÓN 1: Usando phpMyAdmin (Más fácil)")
    print("-" * 70)
    print("1. Abre WAMP y accede a phpMyAdmin: http://localhost/phpmyadmin")
    print("2. Selecciona tu base de datos en el panel izquierdo")
    print("3. Haz clic en la pestaña 'Exportar'")
    print("4. Selecciona:")
    print("   - Método: Rápido")
    print("   - Formato: SQL")
    print("5. Haz clic en 'Continuar'")
    print("6. Se descargará un archivo .sql")
    print("7. Comparte ese archivo con tu compañero\n")
    
    print("OPCIÓN 2: Usando mysqldump (Línea de comandos)")
    print("-" * 70)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_sql = f"backup_dulceria_{timestamp}.sql"
    
    print("Ejecuta este comando en tu terminal:")
    print(f"\nmysqldump -u root -p dulceria_db > {output_sql}\n")
    print("(Reemplaza 'dulceria_db' con el nombre de tu base de datos)")
    print("(Si no tiene contraseña, omite el -p)\n")

def create_readme():
    """Crear archivo README para el compañero"""
    print_header("📝 Creando Instrucciones de Importación")
    
    readme_content = """# 📦 Archivos para Importar

## Contenido
Este paquete contiene los datos del proyecto Dulcería para que puedas configurar tu entorno.

## Instrucciones Rápidas

### 1. Clonar el repositorio (si no lo has hecho)
```bash
git clone [URL_REPOSITORIO]
cd ProyectoIntegrado_Dulceria_VD_PJ/dulceria
```

### 2. Configurar entorno
```bash
python -m venv venv
venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
```

### 3. Configurar MySQL en WAMP
- Inicia WAMP
- Crea una base de datos llamada `dulceria_db` en phpMyAdmin

### 4. Importar los datos

#### Si tienes el archivo .sql:
1. Ve a phpMyAdmin
2. Selecciona la base de datos `dulceria_db`
3. Pestaña "Importar"
4. Selecciona el archivo .sql
5. Haz clic en "Continuar"

#### Si tienes el archivo JSON (fixtures):
```bash
python manage.py migrate
python manage.py loaddata fixtures/datos_compartidos_[timestamp].json
```

### 5. Crear usuarios de prueba
```bash
python manage.py create_test_users
```

### 6. Verificar configuración
```bash
python verificar_configuracion.py
```

### 7. Iniciar servidor
```bash
python manage.py runserver
```

## Usuarios de Prueba
- **Admin**: admin / admin123
- **Gerente**: gerente / gerente123
- **Empleado**: empleado / empleado123

## ¿Problemas?
Lee el archivo `GUIA_CONFIGURACION_COMPAÑERO.md` para más detalles.
"""
    
    try:
        with open("INSTRUCCIONES_IMPORTAR.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)
        print_success("Archivo 'INSTRUCCIONES_IMPORTAR.txt' creado")
        return True
    except Exception as e:
        print_error(f"Error al crear instrucciones: {str(e)}")
        return False

def show_summary():
    """Mostrar resumen final"""
    print_header("📋 RESUMEN - Archivos para Compartir")
    
    print("\n¿Qué compartir con tu compañero?\n")
    
    print("ARCHIVOS OBLIGATORIOS:")
    print("  ✓ Todo el código (vía Git/GitHub)")
    print("  ✓ requirements.txt (ya está en el repo)")
    print("  ✓ GUIA_CONFIGURACION_COMPAÑERO.md (recién creado)")
    print("  ✓ verificar_configuracion.py (recién creado)")
    
    print("\nDATOS DE LA BASE DE DATOS (Elige UNA opción):")
    print("  OPCIÓN A: Archivo .sql de MySQL")
    print("    - Exporta desde phpMyAdmin (Recomendado)")
    print("    - O usa mysqldump")
    print("  OPCIÓN B: Archivo JSON fixtures")
    print("    - Archivo generado en: fixtures/datos_compartidos_*.json")
    
    print("\nINSTRUCCIONES PARA TU COMPAÑERO:")
    print("  1. Clona el repositorio de GitHub")
    print("  2. Lee GUIA_CONFIGURACION_COMPAÑERO.md")
    print("  3. Importa los datos (opción A o B)")
    print("  4. Ejecuta: python manage.py create_test_users")
    print("  5. Ejecuta: python verificar_configuracion.py")
    print("  6. Ejecuta: python manage.py runserver")
    
    print("\n" + "="*70)
    print_success("¡Listo para compartir! 🚀")
    print("="*70 + "\n")

def main():
    print_header("🍬 EXPORTAR PROYECTO DULCERÍA PARA COMPARTIR")
    
    print("\nEste script te ayudará a preparar los archivos para compartir")
    print("con tu compañero de proyecto.\n")
    
    # 1. Exportar fixtures
    fixture_file = export_fixtures()
    
    # 2. Instrucciones para MySQL
    export_mysql_dump()
    
    # 3. Crear README de importación
    create_readme()
    
    # 4. Mostrar resumen
    show_summary()
    
    if fixture_file:
        print(f"\n💡 TIP: El archivo JSON es más fácil de compartir por Git")
        print(f"    Puedes hacer commit del archivo: {fixture_file}")
        print(f"    Tu compañero solo necesitará ejecutar:")
        print(f"    python manage.py loaddata {fixture_file}\n")

if __name__ == "__main__":
    try:
        # Verificar que estamos en el directorio correcto
        if not os.path.exists("manage.py"):
            print_error("Error: Debes ejecutar este script desde el directorio 'dulceria/'")
            sys.exit(1)
        
        main()
        
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print_error(f"\nError inesperado: {str(e)}")
        sys.exit(1)

