# 🔧 Solución: Error 502 Bad Gateway en AWS

## ❌ Problema

Al acceder a la aplicación desde AWS (usando PuTTY o navegador), aparece el error:
```
502 Bad Gateway
nginx
```

## 🔍 Causas Comunes

El error 502 Bad Gateway significa que **nginx está funcionando**, pero **no puede comunicarse con el servidor de aplicación** (gunicorn). Esto puede deberse a:

### 1. **Gunicorn no está instalado** ⚠️ MÁS COMÚN
Elastic Beanstalk necesita `gunicorn` para ejecutar aplicaciones Django en producción.

### 2. **El servidor WSGI no está corriendo**
Gunicorn puede no estar iniciando correctamente.

### 3. **Variables de entorno faltantes o incorrectas**
Si faltan variables críticas (como `DJANGO_SECRET_KEY`, `DB_*`, etc.), Django puede fallar al iniciar.

### 4. **Error en el código de Django**
Si hay un error en `settings.py` o en el código, la aplicación puede crashear al iniciar.

### 5. **Problemas de conexión a la base de datos**
Si no puede conectarse a RDS, la aplicación puede fallar.

---

## ✅ Soluciones

### Solución 1: Agregar Gunicorn a requirements.txt

**Paso 1:** Verifica si `gunicorn` está en `requirements.txt`:
```bash
grep gunicorn requirements.txt
```

**Paso 2:** Si NO está, agrégalo:
```bash
echo "gunicorn==21.2.0" >> requirements.txt
```

O edita manualmente `requirements.txt` y agrega:
```
gunicorn==21.2.0
```

**Paso 3:** Vuelve a desplegar en Elastic Beanstalk.

---

### Solución 2: Verificar Logs de Elastic Beanstalk

**Desde la consola AWS:**
1. Ve a **Elastic Beanstalk** → Tu entorno
2. Ve a **Logs** → **Request logs** → **Last 100 lines**
3. Busca errores relacionados con:
   - `gunicorn`
   - `ImportError`
   - `ModuleNotFoundError`
   - `Database connection`
   - `SECRET_KEY`

**Desde PuTTY (SSH):**
```bash
# Conectarte vía SSH
eb ssh tu-entorno

# Ver logs de la aplicación
sudo tail -f /var/log/eb-engine.log

# Ver logs de gunicorn
sudo tail -f /var/log/eb-hooks.log

# Ver logs de nginx
sudo tail -f /var/log/nginx/error.log
```

---

### Solución 3: Verificar Variables de Entorno

**Desde la consola AWS:**
1. Ve a **Elastic Beanstalk** → Tu entorno → **Configuration** → **Software** → **Edit**
2. Verifica que TODAS estas variables estén configuradas:

```
DJANGO_SECRET_KEY=tu_secret_key_aqui
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=tu-env.elasticbeanstalk.com,tu-ip-publica
DB_NAME=proyecto_db
DB_USER=admin
DB_PASSWORD=tu_password
DB_HOST=dulceria-db.c9uk5jvpenlv.us-east-1.rds.amazonaws.com
DB_PORT=3306
DJANGO_LANGUAGE_CODE=es-cl
DJANGO_TIME_ZONE=America/Santiago
```

**⚠️ IMPORTANTE:** 
- `ALLOWED_HOSTS` debe incluir la IP pública o dominio que estás usando
- Si usas la IP `34.195.100.122`, agrégalo: `ALLOWED_HOSTS=34.195.100.122,tu-env.elasticbeanstalk.com`

---

### Solución 4: Verificar Estado del Servidor WSGI

**Desde PuTTY (SSH):**
```bash
# Conectarte vía SSH
eb ssh tu-entorno

# Verificar si gunicorn está corriendo
ps aux | grep gunicorn

# Si NO está corriendo, verificar el proceso supervisor
sudo systemctl status supervisord

# Ver logs de supervisord
sudo tail -f /var/log/supervisor/supervisord.log
```

---

### Solución 5: Probar la Aplicación Manualmente

**Desde PuTTY (SSH):**
```bash
# Conectarte vía SSH
eb ssh tu-entorno

# Activar el entorno virtual
source /var/app/venv/*/bin/activate

# Ir al directorio de la aplicación
cd /var/app/current

# Verificar que Django puede iniciar
python manage.py check

# Probar conexión a la base de datos
python manage.py dbshell

# Si todo está bien, probar ejecutar gunicorn manualmente
gunicorn dulceria.wsgi:application --bind 127.0.0.1:8000
```

Si gunicorn inicia correctamente, el problema puede ser la configuración de Elastic Beanstalk.

---

### Solución 6: Crear Archivo de Configuración para Gunicorn

Crea un archivo `.ebextensions/01_gunicorn.config`:

```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: dulceria/wsgi.py
    NumProcesses: 2
    NumThreads: 15
```

Y asegúrate de que `.ebextensions/02_database_setup.config` tenga la configuración de WSGI:

```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: dulceria/wsgi.py
```

---

### Solución 7: Verificar Archivos Estáticos

**Desde PuTTY (SSH):**
```bash
# Verificar que collectstatic se ejecutó
ls -la /var/app/current/staticfiles/

# Si no existe, ejecutarlo manualmente
source /var/app/venv/*/bin/activate
cd /var/app/current
python manage.py collectstatic --noinput
```

---

## 🔍 Diagnóstico Rápido

Ejecuta estos comandos en orden para diagnosticar:

```bash
# 1. Conectarte vía SSH
eb ssh tu-entorno

# 2. Verificar gunicorn
ps aux | grep gunicorn

# 3. Ver logs de errores
sudo tail -50 /var/log/nginx/error.log
sudo tail -50 /var/log/eb-engine.log

# 4. Verificar variables de entorno
env | grep DJANGO
env | grep DB_

# 5. Probar Django
source /var/app/venv/*/bin/activate
cd /var/app/current
python manage.py check
```

---

## 📋 Checklist de Verificación

- [ ] `gunicorn` está en `requirements.txt`
- [ ] Todas las variables de entorno están configuradas en Elastic Beanstalk
- [ ] `ALLOWED_HOSTS` incluye la IP/dominio que estás usando
- [ ] La base de datos RDS está accesible desde el security group
- [ ] El archivo `.ebextensions/02_database_setup.config` tiene `WSGIPath: dulceria/wsgi.py`
- [ ] Los logs no muestran errores críticos
- [ ] Gunicorn está corriendo (`ps aux | grep gunicorn`)

---

## 🚨 Si Nada Funciona

1. **Revisa los logs completos:**
   ```bash
   eb logs --all
   ```

2. **Reinicia el entorno:**
   - Desde la consola: **Actions** → **Restart App Server(s)**
   - O desde CLI: `eb restart`

3. **Verifica el health del entorno:**
   - En la consola de Elastic Beanstalk, verifica el estado del entorno
   - Si está en "Degraded" o "Severe", revisa los eventos

4. **Considera recrear el entorno:**
   - Si el problema persiste, puede ser más rápido recrear el entorno desde cero

---

## 📝 Notas Adicionales

- El error 502 generalmente aparece **inmediatamente** al acceder, lo que indica que nginx está funcionando pero el backend no
- Si ves un error 500, el problema es diferente (aplicación corriendo pero con error)
- Siempre verifica los logs ANTES de hacer cambios
