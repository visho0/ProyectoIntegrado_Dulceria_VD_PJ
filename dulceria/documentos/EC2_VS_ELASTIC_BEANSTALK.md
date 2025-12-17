# EC2 vs Elastic Beanstalk - ¿Qué estás usando?

## 🔍 Situación Actual

Estás usando **EC2 directamente** (acceso por PuTTY, IP: `34.195.100.122`). Esto significa:
- ✅ Tienes control total sobre el servidor
- ✅ Ya está funcionando
- ✅ Puedes seguir así sin problemas

## 📊 Comparación

### EC2 Directo (Lo que tienes ahora)
**Ventajas:**
- ✅ Control total
- ✅ Ya está configurado y funcionando
- ✅ Más simple para proyectos pequeños
- ✅ No necesitas aprender Elastic Beanstalk

**Desventajas:**
- ❌ Debes gestionar actualizaciones manualmente
- ❌ No hay auto-scaling automático
- ❌ Debes configurar nginx/gunicorn manualmente

### Elastic Beanstalk
**Ventajas:**
- ✅ Despliegues automáticos
- ✅ Auto-scaling
- ✅ Gestión simplificada
- ✅ Health monitoring automático

**Desventajas:**
- ❌ Requiere configuración inicial
- ❌ Menos control directo
- ❌ Curva de aprendizaje

---

## ✅ Opción 1: Seguir con EC2 (Recomendado si ya funciona)

Si tu aplicación ya está funcionando en EC2, **puedes seguir así**. Solo necesitas:

### Configurar Gunicorn y Nginx manualmente

**1. Verificar que gunicorn esté instalado:**
```bash
# En PuTTY
pip install gunicorn
# O si usas requirements.txt
pip install -r requirements.txt
```

**2. Crear servicio systemd para gunicorn:**

Crea el archivo `/etc/systemd/system/gunicorn.service`:

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Contenido:
```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=admin
Group=www-data
WorkingDirectory=/home/admin/ProyectoIntegrado_Dulceria_VD_PJ/dulceria
ExecStart=/home/admin/ProyectoIntegrado_Dulceria_VD_PJ/dulceria/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/home/admin/ProyectoIntegrado_Dulceria_VD_PJ/dulceria/gunicorn.sock \
          dulceria.wsgi:application

[Install]
WantedBy=multi-user.target
```

**3. Configurar Nginx:**

Crea el archivo `/etc/nginx/sites-available/dulceria`:

```bash
sudo nano /etc/nginx/sites-available/dulceria
```

Contenido:
```nginx
server {
    listen 80;
    server_name 34.195.100.122;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/admin/ProyectoIntegrado_Dulceria_VD_PJ/dulceria;
    }
    
    location /media/ {
        root /home/admin/ProyectoIntegrado_Dulceria_VD_PJ/dulceria;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/admin/ProyectoIntegrado_Dulceria_VD_PJ/dulceria/gunicorn.sock;
    }
}
```

**4. Activar y reiniciar servicios:**
```bash
# Habilitar sitio nginx
sudo ln -s /etc/nginx/sites-available/dulceria /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Habilitar y iniciar gunicorn
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

---

## 🚀 Opción 2: Migrar a Elastic Beanstalk (Opcional)

Si quieres automatizar el despliegue, puedes crear un entorno de Elastic Beanstalk:

### Pasos para crear Elastic Beanstalk

**1. Desde la consola AWS:**
- Ve a **Services → Elastic Beanstalk**
- Click en **Create application**

**2. Configuración:**
- **Application name**: `dulceria`
- **Platform**: Python 3.12
- **Application code**: Upload your code (sube un ZIP de tu proyecto)

**3. Configurar variables de entorno:**
- Ve a **Configuration → Software → Environment properties**
- Agrega todas las variables del `.env`

**4. Desplegar:**
- Sube tu código como ZIP
- Espera a que se despliegue

---

## 💡 Recomendación

**Si tu aplicación ya funciona en EC2:**
- ✅ **Sigue con EC2** - Es más simple y ya está funcionando
- Solo asegúrate de tener gunicorn configurado correctamente
- Configura nginx para que apunte a gunicorn

**Si quieres automatización:**
- Considera Elastic Beanstalk para despliegues más fáciles
- Pero requiere tiempo de configuración inicial

---

## 🔧 Verificar tu configuración actual en EC2

Ejecuta estos comandos en PuTTY para ver qué tienes:

```bash
# Ver si gunicorn está instalado
which gunicorn
pip list | grep gunicorn

# Ver si nginx está corriendo
sudo systemctl status nginx

# Ver procesos de Python/Django
ps aux | grep python
ps aux | grep gunicorn

# Ver configuración de nginx
sudo nginx -t
cat /etc/nginx/sites-enabled/default
```

---

## 📝 Nota Importante

Los archivos `.ebextensions/` que creamos son **solo para Elastic Beanstalk**. Si sigues usando EC2, no los necesitas, pero tampoco hacen daño si están en el repositorio.
