# Sistema de Gestión de Dulcería

Sistema completo de gestión para una dulcería desarrollado con Django, que incluye catálogo de productos, sistema de alertas, gestión de organizaciones y dispositivos.

## 🚀 Inicio Rápido

### Instalación Automática (Recomendado)

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd ProyectoIntegrado_Dulceria_VD_PJ/dulceria

# 2. Crear entorno virtual e instalar dependencias
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt

# 3. Crear base de datos 'dulceria_db' en phpMyAdmin (WAMP)

# 4. Configuración automática (migraciones + datos + usuarios)
python configurar_proyecto.py

# 5. Iniciar servidor
python manage.py runserver
```

**¡Eso es todo!** El proyecto quedará exactamente igual en cualquier PC.

📖 **Guía detallada**: Ver `INICIO_RAPIDO.md`

## Características

- **Catálogo de Productos**: Gestión completa de categorías y productos con imágenes
- **Sistema de Alertas**: Reglas de alerta configurables por producto
- **Gestión de Organizaciones**: Múltiples organizaciones con zonas y dispositivos
- **Mediciones**: Registro de mediciones de dispositivos con jerarquía de fechas
- **Autenticación Multi-Rol**: Sistema de login con roles (Admin, Gerente, Empleado)
- **Admin Django**: Panel de administración completamente configurado
- **Configuración Automática**: Script de setup en un solo comando

## Requisitos

- Python 3.8+
- Django 5.2+
- MySQL (vía WAMP)
- mysqlclient

## 🔐 Usuarios del Sistema

| Usuario | Password | Rol | Acceso |
|---------|----------|-----|--------|
| `admin` | `admin123` | Administrador | Acceso completo |
| `gerente` | `gerente123` | Gerente | Dashboard, Productos |
| `empleado` | `empleado123` | Empleado | Productos |

## Acceso al Sistema

- **URL Principal**: http://127.0.0.1:8000/
- **Admin Django**: http://127.0.0.1:8000/admin/
- **Usuario**: admin
- **Contraseña**: admin123

## Estructura del Proyecto

```
dulceria/
├── dulceria/           # Configuración del proyecto
├── production/         # App principal (productos, alertas, mediciones)
├── organizations/      # App de organizaciones (zonas, dispositivos)
├── accounts/          # App de usuarios y perfiles
├── templates/         # Plantillas HTML
├── fixtures/          # Datos de ejemplo (JSON)
└── static/           # Archivos estáticos
```

## Datos de Ejemplo Incluidos

### Catálogo
- **2 Categorías**: Dulces Tradicionales, Chocolates
- **3 Productos**: Cajeta de Leche, Ate de Guayaba, Chocolate Amargo 70%

### Alertas
- **2 Reglas de Alerta**: Stock Bajo (severidad media), Stock Crítico (severidad alta)
- **6 Relaciones Producto-Alerta**: Cada producto tiene ambas reglas con umbrales personalizados

### Organización Demo
- **1 Organización**: Dulcería Central
- **2 Zonas**: Almacén Principal, Área de Venta
- **3 Dispositivos**: Sensor de Temperatura, Sensor de Humedad, Termómetro Digital

### Mediciones
- **7 Mediciones de ejemplo** con diferentes dispositivos y fechas

## Funcionalidades del Admin

### Maestros
- **Category**: Búsqueda por nombre, filtros por fecha
- **Product**: Columnas con categoría y SKU, filtros por categoría y estado
- **AlertRule**: Filtros por severidad, búsqueda por nombre
- **ProductAlertRule**: Muestra min/max, filtros por severidad

### Por Organización
- **Organization**: Búsqueda por nombre, filtros por fecha
- **Zone**: Columnas con organización, filtros por organización
- **Device**: Columnas con zona y organización, filtros por estado y organización

### Series
- **Measurement**: Jerarquía de fechas (date_hierarchy), orden por fecha descendente

## Configuración de Base de Datos

### SQLite (Por defecto)
No requiere configuración adicional.

### MySQL
1. Descomenta la configuración MySQL en `settings.py`
2. Crea un archivo `.env` con:
   ```
   DB_NAME=dulceria_db
   DB_USER=tu_usuario
   DB_PASSWORD=tu_contraseña
   DB_HOST=localhost
   DB_PORT=3306
   ```

## Comandos Útiles

```bash
# Configuración completa automática (recomendado)
python configurar_proyecto.py

# Verificar que todo esté configurado correctamente
python verificar_configuracion.py

# Crear usuarios de prueba
python manage.py create_test_users

# Exportar datos actuales (si haces cambios)
python manage.py dumpdata --indent 2 --exclude contenttypes --exclude auth.permission -o fixtures/datos_iniciales.json

# Cargar datos iniciales
python manage.py loaddata fixtures/datos_iniciales.json

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario adicional
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

## 📂 Archivos de Configuración

| Archivo | Descripción |
|---------|-------------|
| `configurar_proyecto.py` | Script de configuración automática (todo en uno) |
| `verificar_configuracion.py` | Script para verificar que todo funcione |
| `exportar_para_compartir.py` | Script para exportar datos actuales |
| `fixtures/datos_iniciales.json` | Todos los datos del proyecto |
| `INICIO_RAPIDO.md` | Guía de inicio rápido |
| `GUIA_CONFIGURACION_COMPAÑERO.md` | Guía detallada para configurar |
| `CHECKLIST_INICIO_RAPIDO.md` | Checklist paso a paso |

## 🔄 Compartir el Proyecto

Para compartir el proyecto con otros desarrolladores:

1. **Sube todo a GitHub** (los fixtures ya están incluidos)
2. **Comparte el repositorio**
3. **Ellos ejecutan**:
   ```bash
   git clone <url>
   cd dulceria
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python configurar_proyecto.py
   ```

**¡Todo quedará exactamente igual!** 🎉

## Tecnologías Utilizadas

- **Backend**: Django 5.2
- **Base de Datos**: MySQL (vía WAMP)
- **Frontend**: Bootstrap 5.3, Bootstrap Icons
- **Autenticación**: Django Auth System con roles personalizados
- **Admin**: Django Admin con configuraciones personalizadas

## Licencia

Este proyecto es para fines educativos y de demostración.
