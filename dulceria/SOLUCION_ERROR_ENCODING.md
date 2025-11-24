# 🔧 SOLUCIÓN AL ERROR DE ENCODING

## ❌ Problema Encontrado

El archivo `fixtures/datos_iniciales.json` tiene problemas de encoding que causan el error:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xed in position 1941: invalid continuation byte
```

## ✅ Solución Implementada

### 1. Script Mejorado (`configurar_proyecto.py`)
El script ahora:
- ✅ Intenta cargar `datos_iniciales.json` primero
- ✅ Si falla por encoding, automáticamente usa los fixtures individuales
- ✅ Los fixtures individuales están en UTF-8 y funcionan correctamente

### 2. Cómo Corregir el Encoding (Opcional)

Si quieres corregir el archivo `datos_iniciales.json`, ejecuta en el servidor:

```bash
cd dulceria
python3 corregir_encoding_fixtures.py
```

O manualmente en Python:

```python
import json

# Leer con encoding Windows-1252 o ISO-8859-1
with open('fixtures/datos_iniciales.json', 'r', encoding='windows-1252', errors='replace') as f:
    content = f.read()

# Guardar en UTF-8
with open('fixtures/datos_iniciales.json', 'w', encoding='utf-8') as f:
    f.write(content)
```

## 🚀 Solución Inmediata

**NO necesitas corregir el archivo.** El script ya está configurado para usar los fixtures individuales si el archivo principal falla.

Los fixtures individuales que se cargarán son:
1. `03_organizacion_zona_dispositivo_es.json` - Organizaciones
2. `00_catalogo_categoria_producto_es.json` - Categorías y productos
3. `01_catalogo_alertas_es.json` - Alertas
4. `02_catalogo_producto_alert_es.json` - Relaciones
5. `04_mediciones_ejemplo_es.json` - Mediciones

## ✅ Verificación

Después de ejecutar `configurar_proyecto.py`, deberías ver:
- ✅ Productos cargados: 3 (o más)
- ✅ Categorías: 2
- ✅ Organizaciones: 3

Si aún no se cargan los productos, verifica que los fixtures individuales existan y estén en UTF-8.

