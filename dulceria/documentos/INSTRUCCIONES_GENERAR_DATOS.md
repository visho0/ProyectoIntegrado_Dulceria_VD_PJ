# 📊 INSTRUCCIONES PARA GENERAR DATOS DE PRUEBA

## 🎯 Opción 1: Script Automático (Recomendado)

El script `configurar_proyecto.py` ahora incluye la opción de generar datos automáticamente:

```bash
cd dulceria
python configurar_proyecto.py
```

El script te preguntará si deseas generar los datos de prueba. Responde **"s"** para generar:
- 5,000 proveedores
- 10,000 productos  
- 10,000 movimientos

## 🎯 Opción 2: Variable de Entorno

Para activar automáticamente sin preguntar:

```bash
# Windows (PowerShell)
$env:GENERATE_TEST_DATA="true"
python configurar_proyecto.py

# Windows (CMD)
set GENERATE_TEST_DATA=true
python configurar_proyecto.py

# Linux/Mac
export GENERATE_TEST_DATA=true
python configurar_proyecto.py
```

## 🎯 Opción 3: Comando Manual

Si ya ejecutaste el script antes o solo quieres generar los datos:

```bash
cd dulceria
python manage.py generate_test_data --proveedores 5000 --productos 10000 --movimientos 10000
```

## 🎯 Opción 4: Solo en AWS

Si estás en AWS y solo quieres generar datos (después de aplicar migraciones):

### SSH al servidor:
```bash
eb ssh tu-entorno
```

### Ejecutar comandos:
```bash
cd /var/app/current
python3 manage.py create_categorias_dulces  # Si aún no existen
python3 manage.py generate_test_data --proveedores 5000 --productos 10000 --movimientos 10000
```

## ⚙️ Personalizar Cantidad de Datos

Puedes ajustar las cantidades según necesites:

```bash
# Menos datos (más rápido)
python manage.py generate_test_data --proveedores 100 --productos 1000 --movimientos 500

# Más datos (para pruebas extremas)
python manage.py generate_test_data --proveedores 10000 --productos 20000 --movimientos 20000
```

## ⏱️ Tiempo Estimado

- 100 proveedores + 1,000 productos + 500 movimientos: **~1-2 minutos**
- 5,000 proveedores + 10,000 productos + 10,000 movimientos: **~5-15 minutos**
- 10,000 proveedores + 20,000 productos + 20,000 movimientos: **~15-30 minutos**

## ✅ Verificación

Después de generar los datos, verifica:

```bash
python manage.py shell
```

```python
from production.models import Product, Proveedor, MovimientoInventario, Category
print(f"Categorías: {Category.objects.count()}")        # Debe ser 15
print(f"Proveedores: {Proveedor.objects.count()}")      # Debe ser el número que especificaste
print(f"Productos: {Product.objects.count()}")          # Debe ser el número que especificaste
print(f"Movimientos: {MovimientoInventario.objects.count()}")  # Debe ser el número que especificaste
exit()
```

## 🔍 Buscar Proveedores

Los proveedores generados son completamente buscables:

- **RUT**: `10000001-1`, `10000002-K`, etc.
- **Razón Social**: `Dulces Del Sur 1`, `Confites Del Norte 2`, etc.
- **Email**: `proveedor1@test.com`, `proveedor2@test.com`, etc.
- **Username para login**: `proveedor_0001`, `proveedor_0002`, etc. (password: `test123456`)

## ⚠️ Notas Importantes

1. **No ejecutes múltiples veces** sin necesidad - los datos se acumularán
2. **En producción real** - NO uses datos de prueba, carga datos reales
3. **Tiempo de generación** - Sea paciente, puede tardar varios minutos
4. **Verifica que existan** categorías antes de generar productos

## 🔄 Regenerar Datos (Eliminar y Crear de Nuevo)

Si quieres empezar desde cero:

```python
# En Django shell
from production.models import Product, Proveedor, MovimientoInventario
Product.objects.all().delete()
Proveedor.objects.all().delete()
MovimientoInventario.objects.all().delete()
```

Luego ejecuta el comando de generación nuevamente.

