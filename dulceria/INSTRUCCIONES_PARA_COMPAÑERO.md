# 📦 Instrucciones para Tu Compañero de Equipo

## 🎯 Objetivo

Cuando descargues este proyecto de GitHub en tu computador, verás **EXACTAMENTE lo mismo** que el computador original. No hay diferencias, no hay restricciones.

---

## ⚡ Instalación Rápida

### Paso 1: Descargar el Proyecto

```bash
git clone [URL_DEL_REPOSITORIO]
cd ProyectoIntegrado_Dulceria_VD_PJ/dulceria
```

### Paso 2: Configurar Entorno Python

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows PowerShell)
.\venv\Scripts\Activate.ps1
# Activar entorno (Git Bash)
source venv/Scripts/activate
# Instalar todas las dependencias
pip install -r requirements.txt
```

### Paso 3: Configurar MySQL

1. **Inicia WAMP** (el ícono debe estar verde 🟢)
2. **Abre phpMyAdmin**: http://localhost/phpmyadmin
3. **Crea una base de datos nueva** llamada: `dulceria_db`
4. **NO importes nada manualmente** - el siguiente paso lo hace automáticamente

### Paso 4: Configuración Automática

```bash
python configurar_proyecto.py
```

Este comando hace TODO automáticamente:
- ✅ Crea las tablas en la base de datos
- ✅ Importa TODOS los datos (productos, categorías, organizaciones, etc.)
- ✅ Crea los usuarios con sus contraseñas
- ✅ Configura los perfiles de usuario
- ✅ Verifica que todo esté correcto

**Espera a que termine** (toma 10-20 segundos).

### Paso 5: Iniciar el Servidor

```bash
python manage.py runserver
```

Abre tu navegador en: **http://127.0.0.1:8000**

---

## 🔐 Usuarios que Puedes Usar

Estos usuarios ya están creados y listos para usar:

| Usuario | Contraseña | Rol | Puede Acceder A |
|---------|------------|-----|-----------------|
| `admin` | `admin123` | Administrador | • Dashboard<br>• Productos (ver, crear, editar)<br>• Admin Django<br>• Todo el sistema |
| `gerente` | `gerente123` | Gerente | • Dashboard<br>• Productos (ver, crear, editar)<br>• Admin Django |
| `empleado` | `empleado123` | Empleado | • Lista de Productos (solo ver)<br>• Sin acceso al Admin |

---

## 🌐 URLs del Sistema

Una vez que el servidor esté corriendo:

| URL | Descripción |
|-----|-------------|
| http://127.0.0.1:8000 | Redirige al login |
| http://127.0.0.1:8000/login/ | Pantalla de login |
| http://127.0.0.1:8000/dashboard/ | Dashboard principal (requiere login) |
| http://127.0.0.1:8000/products/ | Lista de productos |
| http://127.0.0.1:8000/products/create/ | Crear nuevo producto |
| http://127.0.0.1:8000/admin/ | Panel de administración Django |

---

## ✅ Verás Exactamente Lo Mismo

### Organizaciones
- ✓ Fábrica
- ✓ Sucursal 1 Mall Plaza
- ✓ Dulcería Central

### Productos
- ✓ Cajeta de Leche
- ✓ Ate de Guayaba
- ✓ Chocolate Amargo 70%
- ✓ Y más...

### Categorías
- ✓ Dulces Tradicionales
- ✓ Chocolates

### Zonas y Dispositivos
- ✓ Almacén Principal
- ✓ Área de Venta
- ✓ Sensores de temperatura y humedad

**Todo esto YA ESTÁ en la base de datos después de ejecutar `configurar_proyecto.py`**

---

## 🔍 Verificar que Todo Funcione

Si quieres verificar que todo esté configurado correctamente:

```bash
python verificar_configuracion.py
```

Este script revisa:
- ✅ Conexión a MySQL
- ✅ Tablas creadas
- ✅ Usuarios existentes
- ✅ Perfiles de usuario configurados
- ✅ Organizaciones creadas
- ✅ Productos cargados

Si todo muestra ✅, estás listo para trabajar.

---

## ❓ Preguntas Frecuentes

### ¿Tendré las mismas contraseñas?
**Sí.** Los usuarios `admin`, `gerente`, `empleado` tienen las mismas contraseñas (`admin123`, `gerente123`, `empleado123`).

### ¿Veré los mismos productos?
**Sí.** Todos los productos, categorías y datos están en el archivo `fixtures/datos_iniciales.json` que se carga automáticamente.

### ¿Podré acceder a las mismas vistas?
**Sí.** Los perfiles de usuario se importan con los datos, así que tendrás acceso completo según el usuario que uses.

### ¿Necesito configurar algo manualmente?
**No.** El script `configurar_proyecto.py` hace todo automáticamente.

### ¿Puedo modificar los datos?
**Sí.** Una vez importados, puedes agregar, editar o eliminar productos, usuarios, etc. Son tus datos locales.

### ¿Cómo sincronizo cambios con mi compañero?
Si haces cambios importantes en los datos, puedes exportarlos:
```bash
python manage.py dumpdata --indent 2 --exclude contenttypes --exclude auth.permission -o fixtures/datos_actualizados.json
```
Luego haz commit y push. Tu compañero descarga y ejecuta:
```bash
python manage.py loaddata fixtures/datos_actualizados.json
```

---

## 🆘 Solución de Problemas

### Error: "Can't connect to MySQL server"
**Solución:**
1. Verifica que WAMP esté corriendo (ícono verde)
2. Verifica que MySQL esté activo en WAMP
3. Asegúrate de haber creado la base de datos `dulceria_db`

### Error: "No module named 'mysqlclient'"
**Solución:**
```bash
pip install mysqlclient
```

Si falla en Windows:
```bash
pip install pymysql
```

### Error: "Tu usuario no tiene un perfil asignado"
**Solución:**
```bash
python manage.py create_test_users
```

### No puedo acceder a /dashboard/ o /products/
**Solución:**
1. Verifica que hayas ejecutado `configurar_proyecto.py`
2. Verifica que estés logueado
3. Ejecuta `verificar_configuracion.py` para ver el problema

---

## 📞 Contacto

Si tienes problemas, consulta estos archivos:
- `INICIO_RAPIDO.md` - Guía resumida
- `GUIA_CONFIGURACION_COMPAÑERO.md` - Guía detallada
- `CHECKLIST_INICIO_RAPIDO.md` - Checklist paso a paso

O contacta a tu compañero de proyecto.

---

## 🎉 ¡Listo!

Una vez que completes estos pasos:

1. ✅ El proyecto funciona
2. ✅ Puedes hacer login
3. ✅ Ves todos los datos
4. ✅ Todo se ve igual que en el PC original
5. ✅ No hay restricciones

**¡A trabajar! 🚀**

