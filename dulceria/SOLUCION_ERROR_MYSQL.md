# 🔧 Solución: Error de Acceso a MySQL

## ❌ Error que Recibiste

```
❌ Error en la configuración de BD: (1045, "Access denied for user 'usuario_mysql'@'localhost' (using password: YES)")
```

## ✅ Solución Paso a Paso

### Paso 1: Descargar la Configuración Corregida

```bash
# Ir a la carpeta del proyecto
cd ProyectoIntegrado_Dulceria_VD_PJ

# Descargar los cambios más recientes
git pull origin main
```

**Esto actualizará el archivo `settings.py` con las credenciales correctas de WAMP.**

### Paso 2: Verificar que WAMP Esté Corriendo

1. Abre WAMP
2. Verifica que el ícono esté **VERDE** 🟢
3. Si está amarillo o rojo, haz clic derecho → "Start All Services"

### Paso 3: Crear la Base de Datos Correctamente

1. Abre phpMyAdmin: http://localhost/phpmyadmin
2. En el panel izquierdo, haz clic en **"Nueva"** o **"New"**
3. Nombre de la base de datos: **`dulceria_db`** (todo en minúsculas, exactamente así)
4. Cotejamiento: `utf8mb4_general_ci` (opcional)
5. Haz clic en **"Crear"**

**⚠️ IMPORTANTE:** El nombre debe ser exactamente `dulceria_db` (no `Dulceria_BD`)

### Paso 4: Verificar las Credenciales de MySQL en WAMP

Por defecto, WAMP usa:
- **Usuario**: `root`
- **Contraseña**: `` (vacío, sin contraseña)

Si cambiaste estas credenciales, edita el archivo `dulceria/dulceria/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dulceria_db',
        'USER': 'root',        # ← Cambia esto si usas otro usuario
        'PASSWORD': '',        # ← Cambia esto si pusiste contraseña
        'HOST': 'localhost',
        'PORT': '3306',
        ...
    }
}
```

### Paso 5: Ejecutar la Configuración Automática

```bash
# Ir a la carpeta dulceria
cd dulceria

# Activar el entorno virtual
.\venv\Scripts\Activate.ps1

# Ejecutar la configuración
python configurar_proyecto.py
```

Ahora debería funcionar correctamente.

---

## 🔍 Verificación Manual

Si aún tienes problemas, verifica cada punto:

### ✅ Checklist de Verificación

- [ ] WAMP está corriendo (ícono verde)
- [ ] Base de datos `dulceria_db` existe en phpMyAdmin
- [ ] El nombre es exactamente `dulceria_db` (minúsculas)
- [ ] Hiciste `git pull origin main` para descargar settings.py actualizado
- [ ] El usuario de MySQL es `root`
- [ ] La contraseña de MySQL está vacía

### 🧪 Probar Conexión Manualmente

Si quieres verificar que puedes conectarte a MySQL, ejecuta esto en Python:

```bash
python
```

Luego en la consola de Python:

```python
import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='dulceria_db'
    )
    print("✅ Conexión exitosa!")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
```

Si ves "✅ Conexión exitosa!", entonces el problema está resuelto.

---

## 🆘 Problemas Comunes

### Problema 1: "Base de datos 'dulceria_db' no existe"

**Solución:**
- Ve a phpMyAdmin
- Crea la base de datos con el nombre exacto: `dulceria_db`

### Problema 2: "Access denied for user 'root'@'localhost'"

**Solución:**
- Abre phpMyAdmin
- Ve a "Cuentas de usuario" / "User accounts"
- Busca el usuario `root` con host `localhost`
- Verifica que no tenga contraseña
- Si tiene contraseña, actualiza `settings.py` con esa contraseña

### Problema 3: WAMP no inicia MySQL

**Solución:**
1. Para todos los servicios de WAMP
2. Reinicia tu computadora
3. Inicia WAMP de nuevo
4. Si sigue fallando, verifica que el puerto 3306 no esté ocupado:
   ```bash
   netstat -ano | findstr :3306
   ```

### Problema 4: "Can't connect to MySQL server"

**Solución:**
- Verifica que el servicio MySQL esté corriendo en WAMP
- En el ícono de WAMP, ve a MySQL → Service → Start/Resume Service

---

## 📋 Resumen de Cambios

### Antes (Error)
```python
'NAME': 'Dulceria_BD',
'USER': 'usuario_mysql',
'PASSWORD': 'contraseña_mysql',
```

### Después (Correcto para WAMP)
```python
'NAME': 'dulceria_db',
'USER': 'root',
'PASSWORD': '',
```

---

## ✅ Una Vez Solucionado

Después de que `configurar_proyecto.py` termine exitosamente:

```bash
# Iniciar el servidor
python manage.py runserver
```

Abre: http://127.0.0.1:8000/login/

**Usuario**: `admin`  
**Contraseña**: `admin123`

---

## 📞 Si Nada Funciona

1. Ejecuta el script de verificación:
   ```bash
   python verificar_configuracion.py
   ```

2. Toma una captura de pantalla del error completo

3. Verifica que:
   - ✅ Descargaste los cambios: `git pull origin main`
   - ✅ La base de datos existe y se llama `dulceria_db`
   - ✅ WAMP está corriendo (ícono verde)
   - ✅ Estás en la carpeta correcta: `ProyectoIntegrado_Dulceria_VD_PJ/dulceria`

---

## 🎉 ¡Listo!

Si seguiste todos los pasos, el error debería estar resuelto y el proyecto funcionando. 🚀

