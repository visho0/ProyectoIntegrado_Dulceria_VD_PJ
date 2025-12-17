# Configuración de Email en AWS (Gmail SMTP)

## 📧 Configuración de Email con Gmail SMTP

Este documento explica cómo configurar el envío de correos electrónicos usando Gmail SMTP tanto en desarrollo local como en producción en AWS.

---

## 🔧 Configuración Local

### 1. Archivo `.env`

El archivo `.env` en la raíz del proyecto (`dulceria/.env`) debe contener las siguientes variables:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion
DEFAULT_FROM_EMAIL=tu_email@gmail.com
SITE_URL=http://localhost:8000
SITE_NAME=Sistema de Gestión Dulcería
```

### 2. Obtener Contraseña de Aplicación de Gmail

1. Ve a: https://myaccount.google.com/apppasswords
2. Selecciona:
   - **Aplicación**: Correo
   - **Dispositivo**: Otro (nombre personalizado) → "Django App"
3. Haz clic en **Generar**
4. Copia la contraseña de 16 caracteres (sin espacios)
5. Reemplaza `EMAIL_HOST_PASSWORD` en el `.env` con esta contraseña

### 3. Reemplazar Email

Reemplaza `TU_EMAIL@gmail.com` en el archivo `.env` con tu email de Gmail real.

---

## ☁️ Configuración en AWS Elastic Beanstalk

### Paso 1: Configurar Variables de Entorno en Elastic Beanstalk

1. Ve a la consola de AWS Elastic Beanstalk
2. Selecciona tu entorno (ej: `dulceria-prod`)
3. Ve a **Configuration** → **Software** → **Edit**
4. En **Environment properties**, agrega las siguientes variables:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion
DEFAULT_FROM_EMAIL=tu_email@gmail.com
SITE_URL=https://tu-dominio.com
SITE_NAME=Sistema de Gestión Dulcería
```

**⚠️ IMPORTANTE:**
- Reemplaza `tu_email@gmail.com` con tu email de Gmail real
- Reemplaza `tu_contraseña_de_aplicacion` con la contraseña de aplicación de 16 caracteres (sin espacios)
- Reemplaza `https://tu-dominio.com` con la URL real de tu aplicación en producción

### Paso 2: Aplicar Cambios

1. Haz clic en **Apply**
2. Espera a que el entorno se actualice (puede tardar 2-5 minutos)
3. Verifica los logs para asegurarte de que no hay errores

---

## 🔒 Seguridad

### Variables Sensibles en AWS

Para mayor seguridad, considera usar **AWS Systems Manager Parameter Store** o **AWS Secrets Manager** en lugar de variables de entorno planas:

1. **Parameter Store** (recomendado para este caso):
   ```bash
   aws ssm put-parameter \
     --name "/dulceria/email/password" \
     --value "tu_contraseña_de_aplicacion" \
     --type "SecureString"
   ```

2. Luego referencia en Elastic Beanstalk usando:
   ```
   EMAIL_HOST_PASSWORD={{resolve:ssm:/dulceria/email/password}}
   ```

### Alternativa: Usar Secrets Manager

Para proyectos más grandes, considera usar AWS Secrets Manager con rotación automática.

---

## ✅ Verificación

### Probar en Desarrollo Local

1. Asegúrate de que el archivo `.env` esté configurado correctamente
2. Ejecuta el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```
3. Prueba crear un usuario o solicitar recuperación de contraseña
4. Verifica que recibas el correo en tu bandeja de entrada

### Probar en Producción (AWS)

1. Despliega los cambios en Elastic Beanstalk
2. Verifica que las variables de entorno estén configuradas correctamente
3. Prueba crear un usuario o solicitar recuperación de contraseña
4. Verifica los logs de Elastic Beanstalk si hay errores:
   ```bash
   eb logs
   ```

---

## 🚨 Troubleshooting

### Error: "SMTPAuthenticationError"

**Causa**: Credenciales incorrectas o contraseña de aplicación inválida.

**Solución**:
- Verifica que la contraseña de aplicación sea correcta (16 caracteres, sin espacios)
- Asegúrate de que la verificación en 2 pasos esté habilitada en Gmail
- Genera una nueva contraseña de aplicación si es necesario

### Error: "Connection refused" o timeout

**Causa**: Firewall o security group bloqueando el puerto 587.

**Solución**:
- Verifica que el security group de EC2 permita tráfico saliente en el puerto 587
- En AWS, los security groups por defecto permiten todo el tráfico saliente, pero verifica si tienes reglas restrictivas

### Los correos no llegan

**Causa**: Límite de Gmail alcanzado o correos en spam.

**Solución**:
- Gmail personal tiene límite de ~500 correos/día
- Verifica la carpeta de spam
- Considera usar SendGrid o Amazon SES para producción si necesitas más volumen

---

## 📊 Límites de Gmail

- **Cuenta personal**: ~500 correos/día
- **Google Workspace**: Límites más altos según el plan

Para producción con alto volumen, considera:
- **SendGrid**: 100 correos/día gratis, luego planes de pago
- **Amazon SES**: Muy económico, 62,000 correos/mes gratis si estás en EC2

---

## 📝 Notas Adicionales

- El archivo `.env` está en `.gitignore` y **NO** debe subirse al repositorio
- Usa `.env.example` como plantilla para otros desarrolladores
- En producción, siempre usa HTTPS para `SITE_URL`
- Considera implementar cola de correos (Celery + Redis) para envíos asíncronos si el volumen es alto

---

## 🔄 Actualización de Configuración

Si necesitas cambiar la configuración de email:

1. **Desarrollo**: Edita el archivo `.env` local
2. **Producción**: Actualiza las variables de entorno en Elastic Beanstalk
3. Reinicia la aplicación si es necesario
