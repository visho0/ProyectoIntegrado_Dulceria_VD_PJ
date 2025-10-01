# Sistema de Gestión de Dulcería

Sistema completo de gestión para una dulcería desarrollado con Django, que incluye catálogo de productos, sistema de alertas, gestión de organizaciones y dispositivos.

## Características

- **Catálogo de Productos**: Gestión completa de categorías y productos
- **Sistema de Alertas**: Reglas de alerta configurables por producto
- **Gestión de Organizaciones**: Múltiples organizaciones con zonas y dispositivos
- **Mediciones**: Registro de mediciones de dispositivos con jerarquía de fechas
- **Autenticación**: Sistema de login/logout con perfiles de usuario
- **Admin Django**: Panel de administración completamente configurado

## Requisitos

- Python 3.8+
- Django 5.2+

## Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd dulceria
   ```

2. **Instalar dependencias**:
   ```bash
   pip install django
   ```

3. **Configurar base de datos**:
   - Por defecto usa SQLite (no requiere configuración adicional)
   - Para MySQL, descomenta la configuración en `settings.py` y crea un archivo `.env`

4. **Aplicar migraciones**:
   ```bash
   python manage.py migrate
   ```

5. **Cargar datos de ejemplo**:
   ```bash
   python manage.py loaddata fixtures/03_organizacion_zona_dispositivo_es.json
   python manage.py loaddata fixtures/00_catalogo_categoria_producto_es.json
   python manage.py loaddata fixtures/01_catalogo_alertas_es.json
   python manage.py loaddata fixtures/02_catalogo_producto_alert_es.json
   python manage.py loaddata fixtures/04_mediciones_ejemplo_es.json
   ```

6. **Configurar usuario administrador**:
   ```bash
   python manage.py setup_admin
   ```

7. **Ejecutar servidor**:
   ```bash
   python manage.py runserver
   ```

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
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Cargar todos los fixtures
python manage.py loaddata fixtures/03_organizacion_zona_dispositivo_es.json
python manage.py loaddata fixtures/00_catalogo_categoria_producto_es.json
python manage.py loaddata fixtures/01_catalogo_alertas_es.json
python manage.py loaddata fixtures/02_catalogo_producto_alert_es.json
python manage.py loaddata fixtures/04_mediciones_ejemplo_es.json

# Configurar admin
python manage.py setup_admin

# Crear superusuario
python manage.py createsuperuser
```

## Tecnologías Utilizadas

- **Backend**: Django 5.2
- **Base de Datos**: SQLite (configurable a MySQL)
- **Frontend**: Bootstrap 5.3, Bootstrap Icons
- **Autenticación**: Django Auth System
- **Admin**: Django Admin con configuraciones personalizadas

## Licencia

Este proyecto es para fines educativos y de demostración.
