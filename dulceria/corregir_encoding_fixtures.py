#!/usr/bin/env python
"""
Script para corregir el encoding de los fixtures
Convierte archivos JSON de Windows-1252/ISO-8859-1 a UTF-8
"""

import os
import json
import sys

def fix_encoding_in_file(filepath):
    """Corregir encoding de un archivo JSON"""
    print(f"Corrigiendo encoding de: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"❌ Archivo no encontrado: {filepath}")
        return False
    
    try:
        # Intentar leer con diferentes encodings
        encodings = ['utf-8', 'windows-1252', 'iso-8859-1', 'latin-1']
        content = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                    used_encoding = encoding
                    print(f"✅ Archivo leído con encoding: {encoding}")
                    break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print(f"❌ No se pudo leer el archivo con ningún encoding conocido")
            return False
        
        # Parsear JSON para validar
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"❌ Error al parsear JSON: {e}")
            return False
        
        # Corregir caracteres comunes mal codificados
        content_fixed = content
        replacements = {
            'Dulcera': 'Dulcería',
            'Fbrica': 'Fábrica',
            'Almacn': 'Almacén',
            'rea': 'Área',
            'exhibicin': 'exhibición',
            'Termmetro': 'Termómetro',
            'Temperatura': 'Temperatura',  # Por si acaso
        }
        
        for old, new in replacements.items():
            if old in content_fixed:
                content_fixed = content_fixed.replace(old, new)
                print(f"  ✓ Corregido: {old} → {new}")
        
        # Validar que el JSON sigue siendo válido después de las correcciones
        try:
            json.loads(content_fixed)
        except json.JSONDecodeError as e:
            print(f"⚠️  Advertencia: JSON modificado puede tener problemas: {e}")
        
        # Guardar en UTF-8
        backup_path = filepath + '.backup'
        if not os.path.exists(backup_path):
            # Crear backup
            with open(backup_path, 'w', encoding=used_encoding) as f:
                f.write(content)
            print(f"✅ Backup creado: {backup_path}")
        
        # Guardar corregido en UTF-8
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content_fixed)
        
        print(f"✅ Archivo guardado en UTF-8: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Corregir encoding de todos los fixtures"""
    print("="*70)
    print("  🔧 CORRECCIÓN DE ENCODING DE FIXTURES")
    print("="*70)
    
    fixtures_dir = "fixtures"
    if not os.path.exists(fixtures_dir):
        print(f"❌ Directorio no encontrado: {fixtures_dir}")
        sys.exit(1)
    
    # Archivos a corregir
    fixtures_files = [
        "fixtures/datos_iniciales.json",
        "fixtures/00_catalogo_categoria_producto_es.json",
        "fixtures/01_catalogo_alertas_es.json",
        "fixtures/02_catalogo_producto_alert_es.json",
        "fixtures/03_organizacion_zona_dispositivo_es.json",
        "fixtures/04_mediciones_ejemplo_es.json",
    ]
    
    success_count = 0
    for fixture_file in fixtures_files:
        if os.path.exists(fixture_file):
            if fix_encoding_in_file(fixture_file):
                success_count += 1
            print()
        else:
            print(f"ℹ️  Archivo no encontrado (opcional): {fixture_file}\n")
    
    print("="*70)
    print(f"✅ Archivos corregidos: {success_count}/{len(fixtures_files)}")
    print("="*70)

if __name__ == "__main__":
    main()

