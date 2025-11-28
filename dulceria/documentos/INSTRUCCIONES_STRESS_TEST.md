# 📋 INSTRUCCIONES RÁPIDAS PARA PRUEBAS DE STRESS

## 🚀 PASOS PARA CONFIGURAR Y PROBAR

### 1. Aplicar Optimizaciones de Base de Datos

```bash
cd dulceria
python manage.py makemigrations production
python manage.py migrate
```

Esto creará los índices optimizados en la base de datos.

### 2. Crear Categorías de Dulces

```bash
python manage.py create_categorias_dulces
```

Esto creará 15 categorías estándar de dulces.

### 3. Generar Datos de Prueba

```bash
# Para cumplir con los objetivos de stress test:
# - ~10,000 productos
# - ~5,000 proveedores  
# - ~10,000 movimientos

python manage.py generate_test_data --proveedores 5000 --productos 10000 --movimientos 10000
```

**Tiempo estimado:** 5-15 minutos dependiendo de la base de datos.

### 4. Verificar Datos Generados

Los proveedores generados tendrán:
- Username: `proveedor_0001`, `proveedor_0002`, etc.
- Password: `test123456`
- RUT válido: `10000001-1`, `10000002-K`, etc.
- Email: `proveedor1@test.com`, `proveedor2@test.com`, etc.

Puedes buscar proveedores usando:
- RUT (ej: `10000001-1`)
- Razón social (ej: `Dulces Del Sur 1`)
- Email (ej: `proveedor1@test.com`)

### 5. Probar Búsquedas y Filtros

#### Productos
- URL: `/products/`
- Buscar por nombre, SKU, categoría
- Probar paginación con 10, 25, 50, 100, 250 registros por página

#### Proveedores  
- URL: `/admin-panel/production/proveedor/`
- Buscar por RUT, razón social, email
- Los proveedores son buscables por todos los campos principales

#### Movimientos
- URL: `/inventario/movimientos/`
- Filtrar por fecha, tipo de movimiento, producto
- Probar con rangos de fechas amplios

## ✅ VERIFICACIÓN DE RENDIMIENTO

### Objetivos a Verificar

1. **Productos (~10,000)**
   - ✅ Búsqueda responde en < 1 segundo
   - ✅ Filtros funcionan correctamente
   - ✅ Paginación fluida sin duplicados ni omisiones
   - ✅ Sin timeouts ni errores 500

2. **Proveedores (~5,000)**
   - ✅ Búsqueda responde en < 1 segundo
   - ✅ Filtros y paginación funcionan correctamente
   - ✅ Sin errores

3. **Movimientos (~10,000)**
   - ✅ Filtros por fecha, tipo, producto funcionan
   - ✅ Resultados consistentes
   - ✅ Tiempos de respuesta aceptables
   - ✅ Sin errores

4. **Concurrencia**
   - Usar JMeter o similar para probar múltiples usuarios simultáneos
   - Verificar estabilidad del sistema
   - Monitorear CPU y memoria

5. **Login en Carga**
   - Probar múltiples logins concurrentes
   - Verificar que no haya caídas
   - Validar rate limiting funciona

## 🔍 COMANDOS ÚTILES

```bash
# Ver cantidad de registros
python manage.py shell
>>> from production.models import Product, Proveedor, MovimientoInventario
>>> print(f"Productos: {Product.objects.count()}")
>>> print(f"Proveedores: {Proveedor.objects.count()}")
>>> print(f"Movimientos: {MovimientoInventario.objects.count()}")
```

## 📝 NOTAS

- Los datos de prueba son ficticios pero válidos
- Los proveedores tienen usuarios asociados que se pueden usar para login
- Los productos están asignados aleatoriamente a categorías
- Los movimientos están distribuidos en los últimos 6 meses

