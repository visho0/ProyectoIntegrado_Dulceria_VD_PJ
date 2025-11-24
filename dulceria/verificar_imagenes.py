#!/usr/bin/env python
"""
Script para verificar imágenes de productos en el servidor
Ejecutar: python3 manage.py shell < verificar_imagenes.py
O copiar y pegar los comandos en el shell
"""

from production.models import Product
import os
from django.conf import settings

print("="*70)
print("VERIFICACIÓN DE IMÁGENES DE PRODUCTOS")
print("="*70)

# Obtener todos los productos
productos = Product.objects.all()

print(f"\nTotal de productos: {productos.count()}\n")

for producto in productos:
    print(f"Producto: {producto.name} (SKU: {producto.sku})")
    print(f"  Estado aprobación: {producto.estado_aprobacion}")
    print(f"  Activo: {producto.is_active}")
    
    if producto.imagen:
        print(f"  Ruta en BD: {producto.imagen}")
        print(f"  Nombre archivo: {producto.imagen.name}")
        
        # Verificar si el archivo existe físicamente
        if hasattr(producto.imagen, 'path'):
            ruta_fisica = producto.imagen.path
            existe = os.path.exists(ruta_fisica)
            print(f"  Ruta física: {ruta_fisica}")
            print(f"  Existe: {'✅ SÍ' if existe else '❌ NO'}")
            
            if existe:
                tamaño = os.path.getsize(ruta_fisica)
                print(f"  Tamaño: {tamaño} bytes")
        else:
            print(f"  Ruta física: No disponible (puede estar en S3)")
        
        # URL que debería funcionar
        print(f"  URL esperada: /media/{producto.imagen.name}")
    else:
        print(f"  Imagen: ❌ No tiene imagen asignada")
    
    print()

# Verificar directorio media
print("="*70)
print("VERIFICACIÓN DEL DIRECTORIO MEDIA")
print("="*70)

media_root = settings.MEDIA_ROOT
print(f"\nMEDIA_ROOT: {media_root}")
print(f"Existe: {'✅ SÍ' if os.path.exists(media_root) else '❌ NO'}")

if os.path.exists(media_root):
    productos_dir = os.path.join(media_root, 'productos')
    print(f"\nDirectorio productos: {productos_dir}")
    print(f"Existe: {'✅ SÍ' if os.path.exists(productos_dir) else '❌ NO'}")
    
    if os.path.exists(productos_dir):
        archivos = os.listdir(productos_dir)
        print(f"Archivos encontrados: {len(archivos)}")
        for archivo in archivos[:10]:  # Mostrar primeros 10
            ruta_completa = os.path.join(productos_dir, archivo)
            tamaño = os.path.getsize(ruta_completa)
            print(f"  - {archivo} ({tamaño} bytes)")

print("\n" + "="*70)

