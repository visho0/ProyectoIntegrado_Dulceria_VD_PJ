# 🔧 INSTRUCCIONES PARA APLICAR MIGRACIONES EN MYSQL

## ⚠️ Problema Resuelto

El error `Specified key was too long; max key length is 1000 bytes` se ha solucionado usando:

1. **Índices con prefijos** para campos de texto largos (primeros 100 caracteres)
2. **Índices compuestos** solo con campos pequeños (Boolean, ForeignKey, etc.)

## 🚀 PASOS PARA APLICAR

### 1. Eliminar la migración problemática (si existe)
```bash
# Si ya intentaste migrar y falló, primero revierte:
python manage.py migrate production 0006
```

### 2. Aplicar las nuevas migraciones
```bash
cd dulceria
python manage.py makemigrations production
python manage.py migrate
```

## ✅ QUÉ SE HA HECHO

### Índices Optimizados para MySQL

#### Productos
- ✅ `prod_name_idx` - Índice en `name(100)` (primeros 100 caracteres)
- ✅ `prod_active_aprob_idx` - Índice compuesto en `is_active`, `estado_aprobacion`
- ✅ `prod_cat_active_idx` - Índice compuesto en `category`, `is_active`
- ✅ SKU ya tiene índice único (no necesita otro)

#### Proveedores
- ✅ `prov_razon_social_idx` - Índice en `razon_social(100)` (primeros 100 caracteres)
- ✅ `prov_email_idx` - Índice en `email(100)` (primeros 100 caracteres)
- ✅ `prov_estado_idx` - Índice en `estado`
- ✅ RUT ya tiene índice único (no necesita otro)

#### Movimientos
- ✅ `mov_tipo_fecha_idx` - Índice compuesto en `tipo`, `fecha DESC`
- ✅ Los demás índices ya existían

## 📝 NOTAS TÉCNICAS

### ¿Por qué prefijos de 100 caracteres?

- MySQL con utf8mb4 usa hasta 4 bytes por carácter
- 100 caracteres × 4 bytes = 400 bytes (muy por debajo del límite de 1000 bytes)
- Es suficiente para búsquedas eficientes (la mayoría de búsquedas usan los primeros caracteres)
- Los primeros 100 caracteres cubren la mayoría de nombres y emails

### ¿Afecta el rendimiento?

**No significativamente:**
- Las búsquedas exactas de nombres completos seguirán funcionando
- Las búsquedas por prefijo (primeros caracteres) serán muy rápidas
- Solo las búsquedas que dependan específicamente del final del string serán más lentas (caso raro)

## 🐛 SI AÚN HAY PROBLEMAS

Si después de aplicar las migraciones aún hay errores:

1. **Verifica que la migración anterior se haya revertido:**
   ```bash
   python manage.py showmigrations production
   ```

2. **Si hay conflictos, elimina manualmente:**
   ```bash
   # Conectar a MySQL y verificar índices existentes
   SHOW INDEX FROM production_product;
   SHOW INDEX FROM production_proveedor;
   SHOW INDEX FROM production_movimientoinventario;
   ```

3. **Eliminar índices problemáticos manualmente (si es necesario):**
   ```sql
   DROP INDEX nombre_indice ON nombre_tabla;
   ```

## ✅ VERIFICACIÓN

Después de aplicar las migraciones, verifica:

```bash
# En MySQL
SHOW INDEX FROM production_product;
SHOW INDEX FROM production_proveedor;
SHOW INDEX FROM production_movimientoinventario;
```

Deberías ver los nuevos índices listados.

¡Las migraciones ahora deberían funcionar correctamente! 🎉

