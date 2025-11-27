# 🔧 SOLUCIÓN AL ERROR DE ÍNDICE DUPLICADO

## ❌ Problema

Error: `Duplicate key name 'mov_tipo_fecha_idx'`

Este error ocurrió porque:
1. La migración **0007** creó los índices mediante SQL personalizado
2. Django detectó los índices en el `Meta` del modelo y generó la migración **0008**
3. La migración 0008 intentó crear índices que ya existían

## ✅ Solución Aplicada

1. **Eliminada la migración 0008** (era redundante)
2. **Eliminados los índices duplicados del `Meta`** de los modelos Product y Proveedor
3. **Mantenidos los índices en MovimientoInventario** que ya existían desde la migración 0005

## 🚀 Pasos para Resolver

### Opción 1: Si la migración 0007 ya se aplicó parcialmente

1. **Verificar qué índices ya existen:**
   ```sql
   SHOW INDEX FROM production_product;
   SHOW INDEX FROM production_proveedor;
   SHOW INDEX FROM production_movimientoinventario;
   ```

2. **Marcar la migración 0007 como aplicada (si los índices ya existen):**
   ```bash
   python manage.py migrate production 0007 --fake
   ```

3. **Aplicar migraciones pendientes:**
   ```bash
   python manage.py migrate
   ```

### Opción 2: Si la migración 0007 NO se aplicó

1. **Aplicar la migración 0007 normalmente:**
   ```bash
   python manage.py migrate production 0007
   ```

   La migración tiene `try/except` por lo que si un índice ya existe, simplemente lo ignora.

2. **Aplicar migraciones pendientes:**
   ```bash
   python manage.py migrate
   ```

### Opción 3: Limpiar e intentar de nuevo

Si aún hay problemas, puedes eliminar manualmente los índices duplicados:

```sql
-- Solo si realmente necesitas eliminarlos
DROP INDEX IF EXISTS mov_tipo_fecha_idx ON production_movimientoinventario;
DROP INDEX IF EXISTS prod_active_aprob_idx ON production_product;
DROP INDEX IF EXISTS prod_cat_active_idx ON production_product;
DROP INDEX IF EXISTS prov_estado_idx ON production_proveedor;
```

Luego ejecutar:
```bash
python manage.py migrate
```

## 📋 Estado Actual

- ✅ Migración 0007 existe y está lista
- ✅ Migración 0008 eliminada (era redundante)
- ✅ Modelos limpiados de índices duplicados
- ⏳ Solo falta aplicar la migración 0007

## 🎯 Próximo Paso

Ejecutar:
```bash
python manage.py migrate
```

La migración 0007 debería aplicarse correctamente ya que tiene protección contra índices duplicados (try/except).

