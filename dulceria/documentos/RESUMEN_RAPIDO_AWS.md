# ⚡ RESUMEN RÁPIDO: Cargar Datos en AWS

## 🎯 Problema
Los cambios visuales se ven, pero no aparecen productos, categorías ni proveedores.

## ✅ Solución Rápida

### Opción A: SSH al Servidor (MÁS RÁPIDO)

```bash
# 1. Conectar
eb ssh tu-entorno

# 2. Ejecutar estos comandos en el servidor:
cd /var/app/current
python3 manage.py migrate                                    # Aplicar migraciones
python3 manage.py create_categorias_dulces                  # Crear categorías
python3 manage.py generate_test_data --proveedores 5000 --productos 10000 --movimientos 10000  # Generar datos

# 3. Verificar
python3 manage.py shell
>>> from production.models import Category, Product, Proveedor
>>> print(f"Categorías: {Category.objects.count()}")       # Debe ser 15
>>> print(f"Productos: {Product.objects.count()}")         # Debe ser ~10000
>>> print(f"Proveedores: {Proveedor.objects.count()}")     # Debe ser ~5000
>>> exit()
```

**⏳ Tiempo estimado:** 5-15 minutos (la generación de datos es lo que más tarda)

### Opción B: Script Automático (PARA EL FUTURO)

He creado el archivo `.ebextensions/02_database_setup.config` que ejecutará estos comandos automáticamente en cada despliegue.

**Para activarlo:**
```bash
git add .ebextensions/02_database_setup.config
git commit -m "Agregar setup automático de base de datos"
eb deploy
```

Esto ejecutará automáticamente:
- ✅ Migraciones
- ✅ Crear categorías
- ✅ Generar datos de prueba (5,000 proveedores, 10,000 productos, 10,000 movimientos)

## 📋 Comandos Necesarios (EJECUTAR EN AWS)

```bash
# En el servidor AWS:
cd /var/app/current
python3 manage.py migrate                                    # Aplicar migraciones
python3 manage.py create_categorias_dulces                  # Crear categorías
python3 manage.py generate_test_data --proveedores 5000 --productos 10000 --movimientos 10000  # Generar datos
```

## ✅ Verificación

Después de ejecutar, verifica en tu sitio:
- `/admin/production/category/` - Debe mostrar 15 categorías
- `/products/` - Debe mostrar ~10,000 productos
- `/admin-panel/production/proveedor/` - Debe mostrar ~5,000 proveedores

## 📝 Notas

- Los datos de desarrollo NO se copian automáticamente a producción
- Debes ejecutar los comandos en el servidor AWS
- La generación de datos puede tardar 5-15 minutos - sé paciente
- Los proveedores son buscables por RUT, razón social y email

## 🚀 Para Desarrollo Local

Ejecuta el script de configuración que ahora incluye generación de datos:

```bash
cd dulceria
python configurar_proyecto.py
```

Responde "s" cuando pregunte si quieres generar datos de prueba.

¡Eso es todo! 🚀

