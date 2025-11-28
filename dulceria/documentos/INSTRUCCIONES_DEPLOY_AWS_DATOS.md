# 🚀 INSTRUCCIONES PARA CARGAR DATOS EN AWS PRODUCCIÓN

## ❌ Problema

Los cambios visuales se ven, pero no aparecen productos, categorías ni proveedores en AWS. Esto es porque:

1. ✅ El código está desplegado
2. ✅ La base de datos está conectada
3. ❌ Las migraciones no están aplicadas
4. ❌ Los datos no están cargados

## ✅ SOLUCIÓN - Pasos a Ejecutar en AWS

### Opción 1: SSH al Servidor (Recomendado)

Si tienes acceso SSH al servidor de Elastic Beanstalk:

```bash
# 1. Conectar al servidor AWS
eb ssh tu-entorno-nombre

# 2. Navegar al directorio de la aplicación
cd /var/app/current

# 3. Activar el entorno virtual (si existe)
source /var/app/venv/*/bin/activate  # O la ruta correcta

# 4. Aplicar migraciones
python manage.py migrate

# 5. Crear categorías de dulces
python manage.py create_categorias_dulces

# 6. (Opcional) Generar datos de prueba
python manage.py generate_test_data --proveedores 100 --productos 1000 --movimientos 500

# 7. Verificar que funcionó
python manage.py shell
>>> from production.models import Product, Category, Proveedor
>>> print(f"Categorías: {Category.objects.count()}")
>>> print(f"Productos: {Product.objects.count()}")
>>> print(f"Proveedores: {Proveedor.objects.count()}")
>>> exit()
```

### Opción 2: Ejecutar Comandos Remotos con EB CLI

```bash
# Desde tu máquina local, ejecutar comandos en el servidor
eb ssh tu-entorno-nombre --command "cd /var/app/current && python manage.py migrate"
eb ssh tu-entorno-nombre --command "cd /var/app/current && python manage.py create_categorias_dulces"
```

### Opción 3: Script de Configuración (.ebextensions)

Crea un script de post-deploy para ejecutar automáticamente después de cada despliegue:

**Archivo: `.ebextensions/02_database_setup.config`**

```yaml
container_commands:
  01_migrate:
    command: "source /var/app/venv/*/bin/activate && python manage.py migrate"
    leader_only: true
  02_create_categories:
    command: "source /var/app/venv/*/bin/activate && python manage.py create_categorias_dulces"
    leader_only: true
```

Luego haz commit y push:

```bash
git add .ebextensions/02_database_setup.config
git commit -m "Agregar script de configuración de base de datos"
eb deploy
```

### Opción 4: Ejecutar desde la Consola de AWS

1. Ve a **Elastic Beanstalk → Tu Entorno → Configuration → Software**
2. Agrega comandos de post-deploy en la sección de comandos
3. O usa **SSH** desde la consola de AWS directamente

## 📋 PASOS PASO A PASO (Recomendado)

### Paso 1: Conectar al Servidor

```bash
# Si usas EB CLI
eb ssh

# O conecta directamente por SSH
ssh ec2-user@tu-ip-o-dominio
```

### Paso 2: Aplicar Migraciones

```bash
cd /var/app/current
python3 manage.py migrate
```

Esto aplicará todas las migraciones pendientes, incluyendo la **0007** con los índices optimizados.

### Paso 3: Crear Categorías

```bash
python3 manage.py create_categorias_dulces
```

Esto creará las 15 categorías estándar de dulces.

### Paso 4: Verificar

```bash
python3 manage.py shell
```

Luego en el shell de Python:
```python
from production.models import Category, Product, Proveedor
print(f"Categorías: {Category.objects.count()}")
print(f"Productos: {Product.objects.count()}")
print(f"Proveedores: {Proveedor.objects.count()}")
exit()
```

### Paso 5: (Opcional) Cargar Datos de Prueba

Si quieres datos de prueba en producción:

```bash
# Cargar datos moderados (ajusta según necesites)
python3 manage.py generate_test_data --proveedores 50 --productos 500 --movimientos 200
```

**⚠️ IMPORTANTE:** En producción real, NO uses datos de prueba. Carga datos reales manualmente o mediante importación.

## 🔍 VERIFICAR QUE FUNCIONÓ

1. **Ve a tu sitio en AWS:**
   - Deberías ver productos, categorías y proveedores

2. **Verifica en Django Admin:**
   - `/admin/production/category/` - Debe mostrar categorías
   - `/admin/production/product/` - Debe mostrar productos
   - `/admin/production/proveedor/` - Debe mostrar proveedores

3. **Verifica en las vistas:**
   - `/products/` - Debe listar productos
   - `/admin-panel/production/proveedor/` - Debe listar proveedores

## ⚠️ PROBLEMAS COMUNES

### Error: "No module named 'production'"

**Solución:** Asegúrate de estar en el directorio correcto:
```bash
cd /var/app/current
# O el directorio donde está tu proyecto
```

### Error: "Can't connect to database"

**Solución:** Verifica las variables de entorno:
```bash
eb printenv
# O
env | grep DB_
```

Asegúrate de que `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` estén configurados correctamente.

### Error: "Table already exists"

**Solución:** Las migraciones ya se aplicaron. Continúa con crear categorías:
```bash
python3 manage.py create_categorias_dulces
```

## 🎯 CHECKLIST FINAL

- [ ] Migraciones aplicadas (`python manage.py migrate`)
- [ ] Categorías creadas (`python manage.py create_categorias_dulces`)
- [ ] Verificadas categorías en admin
- [ ] (Opcional) Datos de prueba cargados
- [ ] Verificado que productos aparecen en `/products/`
- [ ] Verificado que proveedores aparecen en admin

## 📝 NOTAS IMPORTANTES

1. **Datos de Desarrollo vs Producción:**
   - Los datos de tu base de datos local NO se copian automáticamente a AWS
   - Debes ejecutar los comandos arriba en el servidor de AWS

2. **Migraciones:**
   - Las migraciones se deben aplicar en cada entorno (desarrollo y producción)
   - Cada vez que hagas cambios en los modelos, ejecuta `migrate` en producción

3. **Datos Iniciales:**
   - Usa `create_categorias_dulces` para crear categorías estándar
   - Usa el admin o scripts personalizados para datos reales
   - NO uses `generate_test_data` en producción real (solo para pruebas)

¡Ejecuta estos pasos y tus datos deberían aparecer! 🚀

