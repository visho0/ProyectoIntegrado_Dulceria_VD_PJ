# 🖼️ SOLUCIÓN PARA IMÁGENES EN PRODUCCIÓN

## ❌ Problema

Las imágenes de los productos no se muestran en producción (`DEBUG=False`) porque Django no sirve archivos media automáticamente en producción.

## ✅ Solución Aplicada

Se modificó `dulceria/urls.py` para servir archivos media también en producción usando una vista de Django.

### Cambios Realizados

1. **Modificado `dulceria/urls.py`**:
   - Agregada configuración para servir `/media/` en producción
   - Usa `django.views.static.serve` para servir archivos media

## ⚠️ Nota Importante

Esta solución funciona pero **NO es la ideal para producción**. Para producción real, deberías:

### Opción 1: Usar S3 (Recomendado para AWS)
1. Instalar `django-storages` y `boto3`:
   ```bash
   pip install django-storages boto3
   ```

2. Configurar en `settings.py`:
   ```python
   INSTALLED_APPS = [
       # ... otras apps
       'storages',
   ]
   
   # Configuración S3
   AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
   AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
   AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
   AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
   
   # Usar S3 para media files
   DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   ```

3. Subir imágenes a S3

### Opción 2: Configurar Nginx/Apache
Configurar el servidor web para servir `/media/` directamente:

**Nginx:**
```nginx
location /media/ {
    alias /ruta/a/tu/proyecto/media/;
}
```

**Apache:**
```apache
Alias /media/ /ruta/a/tu/proyecto/media/
<Directory /ruta/a/tu/proyecto/media>
    Require all granted
</Directory>
```

## 🔍 Verificación

Después de aplicar los cambios:

1. Reinicia el servidor Django
2. Verifica que las imágenes se muestren en:
   - http://34.195.100.122/products/
   - http://34.195.100.122/media/productos/[nombre-imagen].jpg

3. Si aún no aparecen, verifica:
   - Que los archivos existan en `media/productos/` en el servidor
   - Que los permisos del directorio sean correctos
   - Que la ruta en la base de datos sea correcta

## 📝 Comandos Útiles

### Verificar imágenes en el servidor:
```bash
ls -la media/productos/
```

### Verificar permisos:
```bash
chmod -R 755 media/
```

### Verificar que Django puede leer los archivos:
```bash
python3 manage.py shell
```
```python
from production.models import Product
product = Product.objects.first()
print(product.imagen.path if product.imagen else "Sin imagen")
```

