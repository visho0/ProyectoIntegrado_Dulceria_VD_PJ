# ✅ Checklist de Inicio Rápido - Proyecto Dulcería

Marca cada paso a medida que lo completes:

## 📥 Preparación Inicial

- [ ] WAMP instalado y funcionando (ícono verde)
- [ ] Python 3.8+ instalado
- [ ] Git instalado
- [ ] Repositorio clonado

## 🔧 Configuración del Entorno

```bash
# 1. Ir al directorio del proyecto
cd ProyectoIntegrado_Dulceria_VD_PJ/dulceria
```

- [ ] Estoy en el directorio correcto (donde está `manage.py`)

```bash
# 2. Crear entorno virtual
python -m venv venv
```

- [ ] Entorno virtual creado

```bash
# 3. Activar entorno virtual (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# O en CMD:
venv\Scripts\activate.bat
```

- [ ] Entorno virtual activado (veo `(venv)` en la terminal)

```bash
# 4. Instalar dependencias
pip install -r requirements.txt
```

- [ ] Todas las dependencias instaladas sin errores

## 💾 Configuración de la Base de Datos

### En phpMyAdmin:

- [ ] Abrí phpMyAdmin (http://localhost/phpmyadmin)
- [ ] Creé una base de datos llamada `dulceria_db`

### Importar Datos (elige UNA opción):

**OPCIÓN A: Archivo SQL**
- [ ] Tengo el archivo `.sql` del compañero
- [ ] Lo importé en phpMyAdmin → Importar
- [ ] La importación fue exitosa

**OPCIÓN B: Fixtures JSON**
- [ ] Tengo el archivo JSON en la carpeta `fixtures/`
- [ ] Ejecuté: `python manage.py migrate`
- [ ] Ejecuté: `python manage.py loaddata fixtures/datos_compartidos_*.json`

## 👥 Crear Usuarios

```bash
# Crear usuarios de prueba
python manage.py create_test_users
```

- [ ] Comando ejecutado exitosamente
- [ ] Veo el mensaje de usuarios creados

## ✔️ Verificación

```bash
# Verificar que todo esté configurado
python verificar_configuracion.py
```

- [ ] El script muestra "✅" en todas las verificaciones
- [ ] No hay errores críticos

## 🚀 ¡Listo para Usar!

```bash
# Iniciar el servidor
python manage.py runserver
```

- [ ] Servidor corriendo sin errores
- [ ] Puedo abrir http://127.0.0.1:8000

## 🔐 Probar Accesos

Prueba iniciar sesión con estos usuarios:

**Usuario Admin:**
- URL: http://127.0.0.1:8000/login/
- Username: `admin`
- Password: `admin123`
- [ ] Puedo hacer login
- [ ] Veo el dashboard
- [ ] Puedo acceder a /products/
- [ ] Puedo acceder a /admin/

**Usuario Gerente:**
- Username: `gerente`
- Password: `gerente123`
- [ ] Puedo hacer login
- [ ] Veo el dashboard

**Usuario Empleado:**
- Username: `empleado`
- Password: `empleado123`
- [ ] Puedo hacer login
- [ ] Veo la lista de productos

## ❌ Si algo falla...

1. **Error de conexión a MySQL:**
   - [ ] Verifiqué que WAMP esté corriendo
   - [ ] Verifiqué el servicio MySQL en WAMP
   - [ ] Revisé `settings.py` → DATABASES

2. **"Tu usuario no tiene un perfil asignado":**
   - [ ] Ejecuté: `python manage.py create_test_users`
   - [ ] Verifico en /admin/ que mi usuario tenga un UserProfile

3. **No puedo acceder a vistas (solo a /admin):**
   - [ ] Mi usuario tiene un UserProfile
   - [ ] El UserProfile tiene una Organization asignada
   - [ ] Ejecuté: `python verificar_configuracion.py`

4. **Error "mysqlclient not installed":**
   - [ ] Ejecuté: `pip install mysqlclient`
   - [ ] Si falla, probé: `pip install pymysql`

## 📚 Documentación Adicional

Si necesitas más ayuda, consulta:
- `GUIA_CONFIGURACION_COMPAÑERO.md` - Guía detallada completa
- `README.md` - Documentación del proyecto
- Contacta a tu compañero de equipo

---

## ✨ ¡Todo Listo!

Si marcaste todos los checkboxes principales, ¡estás listo para trabajar!

**Comandos útiles para recordar:**

```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Iniciar servidor
python manage.py runserver

# Ver usuarios
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all()

# Acceder al admin
http://127.0.0.1:8000/admin/
```

¡Feliz desarrollo! 🍬🚀

