# GUÍA PASO A PASO PARA CAPTURAS DE PANTALLA
## Proyecto Dulcería - Evidencias Obligatorias

---

## 🎯 **SECUENCIA DE CAPTURAS RECOMENDADA**

### **FASE 1: CONFIGURACIÓN Y MIGRACIONES**

#### **1.1 Configuración de Base de Datos**
**Archivo:** `dulceria/dulceria/settings.py`
**Líneas:** 80-97
**Acción:** Abrir el archivo y mostrar la configuración DATABASES
**Captura:** Mostrar las líneas 80-97 con la configuración SQLite

#### **1.2 Comando makemigrations**
**Terminal:** 
```bash
cd dulceria
python manage.py makemigrations
```
**Captura:** Salida completa del comando mostrando migraciones creadas

#### **1.3 Comando migrate**
**Terminal:**
```bash
python manage.py migrate
```
**Captura:** Salida completa mostrando "Operations to perform" y "Running migrations"

---

### **FASE 2: SEMILLAS (FIXTURES)**

#### **2.1 Archivos de Fixtures**
**Directorio:** `dulceria/fixtures/`
**Acción:** Mostrar el contenido del directorio
**Captura:** Lista de los 5 archivos JSON

#### **2.2 Contenido de Fixture Principal**
**Archivo:** `dulceria/fixtures/00_catalogo_categoria_producto_es.json`
**Acción:** Abrir el archivo y mostrar el contenido
**Captura:** JSON con las 2 categorías y 3 productos

#### **2.3 Carga de Semillas - Organizaciones**
**Terminal:**
```bash
python manage.py loaddata fixtures/03_organizacion_zona_dispositivo_es.json
```
**Captura:** Salida mostrando "Installed 6 object(s) from 1 fixture(s)"

#### **2.4 Carga de Semillas - Catálogo**
**Terminal:**
```bash
python manage.py loaddata fixtures/00_catalogo_categoria_producto_es.json
```
**Captura:** Salida mostrando "Installed 5 object(s) from 1 fixture(s)"

#### **2.5 Carga de Semillas - Alertas**
**Terminal:**
```bash
python manage.py loaddata fixtures/01_catalogo_alertas_es.json
```
**Captura:** Salida mostrando "Installed 2 object(s) from 1 fixture(s)"

#### **2.6 Carga de Semillas - Relaciones**
**Terminal:**
```bash
python manage.py loaddata fixtures/02_catalogo_producto_alert_es.json
```
**Captura:** Salida mostrando "Installed 6 object(s) from 1 fixture(s)"

#### **2.7 Carga de Semillas - Mediciones**
**Terminal:**
```bash
python manage.py loaddata fixtures/04_mediciones_ejemplo_es.json
```
**Captura:** Salida mostrando "Installed 7 object(s) from 1 fixture(s)"

---

### **FASE 3: CONFIGURACIÓN DE ADMIN**

#### **3.1 Configuración de Admin - Production**
**Archivo:** `dulceria/production/admin.py`
**Líneas:** 1-30
**Acción:** Mostrar la configuración de CategoryAdmin y ProductAdmin
**Captura:** Código con list_display, search_fields, list_filter

#### **3.2 Configuración de Admin - Organizations**
**Archivo:** `dulceria/organizations/admin.py`
**Líneas:** 1-25
**Acción:** Mostrar la configuración de OrganizationAdmin y ZoneAdmin
**Captura:** Código con list_display y list_select_related

#### **3.3 Configuración de Admin - Measurement**
**Archivo:** `dulceria/production/admin.py`
**Líneas:** 80-100
**Acción:** Mostrar MeasurementAdmin con date_hierarchy
**Captura:** Código con date_hierarchy y ordering

---

### **FASE 4: ADMIN BÁSICO FUNCIONANDO**

#### **4.1 Panel Principal del Admin**
**URL:** http://127.0.0.1:8000/admin/
**Acción:** Iniciar servidor y acceder al admin
**Comando:** `python manage.py runserver`
**Captura:** Página principal del admin con todos los modelos registrados

#### **4.2 Category Admin - Lista**
**URL:** http://127.0.0.1:8000/admin/production/category/
**Acción:** Hacer clic en "Categories"
**Captura:** Lista mostrando las 2 categorías con columnas name, created_at, updated_at

#### **4.3 Category Admin - Búsqueda**
**URL:** http://127.0.0.1:8000/admin/production/category/
**Acción:** Usar la caja de búsqueda para buscar "Dulces"
**Captura:** Resultados filtrados por búsqueda

#### **4.4 Product Admin - Lista**
**URL:** http://127.0.0.1:8000/admin/production/product/
**Acción:** Hacer clic en "Products"
**Captura:** Lista mostrando los 3 productos con columnas name, sku, category, price

#### **4.5 Product Admin - Filtro por Categoría**
**URL:** http://127.0.0.1:8000/admin/production/product/
**Acción:** Usar el filtro lateral "Category" para filtrar por "Dulces Tradicionales"
**Captura:** Lista filtrada mostrando solo productos de esa categoría

#### **4.6 AlertRule Admin - Lista**
**URL:** http://127.0.0.1:8000/admin/production/alertrule/
**Acción:** Hacer clic en "Alert rules"
**Captura:** Lista mostrando las 2 reglas con columnas name, severity, min_threshold, max_threshold

#### **4.7 AlertRule Admin - Filtro por Severidad**
**URL:** http://127.0.0.1:8000/admin/production/alertrule/
**Acción:** Usar el filtro lateral "Severity" para filtrar por "medium"
**Captura:** Lista filtrada por severidad

#### **4.8 ProductAlertRule Admin - Lista**
**URL:** http://127.0.0.1:8000/admin/production/productalertrule/
**Acción:** Hacer clic en "Product alert rules"
**Captura:** Lista mostrando las 6 relaciones con columnas product, alert_rule, min_threshold, max_threshold

#### **4.9 Organization Admin - Lista**
**URL:** http://127.0.0.1:8000/admin/organizations/organization/
**Acción:** Hacer clic en "Organizations"
**Captura:** Lista mostrando "Dulcería Central" con columnas name, created_at, updated_at

#### **4.10 Zone Admin - Lista**
**URL:** http://127.0.0.1:8000/admin/organizations/zone/
**Acción:** Hacer clic en "Zones"
**Captura:** Lista mostrando las 2 zonas con columnas name, organization, created_at

#### **4.11 Zone Admin - Filtro por Organización**
**URL:** http://127.0.0.1:8000/admin/organizations/zone/
**Acción:** Usar el filtro lateral "Organization" para filtrar por "Dulcería Central"
**Captura:** Lista filtrada por organización

#### **4.12 Device Admin - Lista**
**URL:** http://127.0.0.1:8000/admin/organizations/device/
**Acción:** Hacer clic en "Devices"
**Captura:** Lista mostrando los 3 dispositivos con columnas name, serial, zone, organization, status

#### **4.13 Device Admin - Filtro por Organización**
**URL:** http://127.0.0.1:8000/admin/organizations/device/
**Acción:** Usar el filtro lateral "Organization" para filtrar por "Dulcería Central"
**Captura:** Lista filtrada por organización

#### **4.14 Measurement Admin - Lista**
**URL:** http://127.0.0.1:8000/admin/production/measurement/
**Acción:** Hacer clic en "Measurements"
**Captura:** Lista mostrando las 7 mediciones con date hierarchy y orden por fecha descendente

#### **4.15 Measurement Admin - Date Hierarchy**
**URL:** http://127.0.0.1:8000/admin/production/measurement/
**Acción:** Hacer clic en el enlace de fecha en el date hierarchy
**Captura:** Vista filtrada por fecha mostrando la jerarquía funcionando

---

### **FASE 5: SISTEMA DE LOGIN/LOGOUT**

#### **5.1 Página de Login**
**URL:** http://127.0.0.1:8000/login/
**Acción:** Acceder a la página de login
**Captura:** Formulario de login personalizado con Bootstrap

#### **5.2 Login Exitoso**
**Acción:** Ingresar usuario "admin" y contraseña "admin123"
**Captura:** Redirección al dashboard después del login

#### **5.3 Dashboard Protegido**
**URL:** http://127.0.0.1:8000/
**Acción:** Verificar que se muestra el dashboard
**Captura:** Dashboard con estadísticas y datos del usuario

#### **5.4 Lista de Productos Protegida**
**URL:** http://127.0.0.1:8000/products/
**Acción:** Navegar a la lista de productos
**Captura:** Lista de productos con filtrado por organización

#### **5.5 Logout**
**Acción:** Hacer clic en "Salir" en el menú
**Captura:** Redirección a la página de login después del logout

---

### **FASE 6: CONFIGURACIÓN DE USUARIO**

#### **6.1 Comando de Configuración**
**Terminal:**
```bash
python manage.py setup_admin
```
**Captura:** Salida del comando mostrando configuración exitosa

#### **6.2 UserProfile en Admin**
**URL:** http://127.0.0.1:8000/admin/accounts/userprofile/
**Acción:** Verificar que existe el perfil del usuario admin
**Captura:** Lista mostrando el perfil asociado a "Dulcería Central"

---

### **FASE 7: ESTRUCTURA DEL PROYECTO**

#### **7.1 Estructura de Directorios**
**Terminal:**
```bash
dir dulceria
```
**Captura:** Lista de directorios y archivos del proyecto

#### **7.2 Archivos de Fixtures**
**Terminal:**
```bash
dir dulceria\fixtures
```
**Captura:** Lista de archivos JSON de fixtures

#### **7.3 Archivo README**
**Archivo:** `dulceria/README.md`
**Acción:** Abrir el archivo README
**Captura:** Contenido del README con instrucciones de instalación

---

## 📋 **CHECKLIST DE CAPTURAS**

### **Configuración (3 capturas):**
- [ ] settings.py - DATABASES
- [ ] makemigrations - salida
- [ ] migrate - salida

### **Semillas (7 capturas):**
- [ ] Archivos de fixtures
- [ ] Contenido de fixture principal
- [ ] Carga organizaciones
- [ ] Carga catálogo
- [ ] Carga alertas
- [ ] Carga relaciones
- [ ] Carga mediciones

### **Admin (15 capturas):**
- [ ] Panel principal
- [ ] Category lista
- [ ] Category búsqueda
- [ ] Product lista
- [ ] Product filtro categoría
- [ ] AlertRule lista
- [ ] AlertRule filtro severidad
- [ ] ProductAlertRule lista
- [ ] Organization lista
- [ ] Zone lista
- [ ] Zone filtro organización
- [ ] Device lista
- [ ] Device filtro organización
- [ ] Measurement lista
- [ ] Measurement date hierarchy

### **Login/Logout (5 capturas):**
- [ ] Página login
- [ ] Login exitoso
- [ ] Dashboard protegido
- [ ] Lista productos protegida
- [ ] Logout

### **Configuración (3 capturas):**
- [ ] Comando setup_admin
- [ ] UserProfile en admin
- [ ] Estructura proyecto

**TOTAL: 33 capturas de pantalla**

---

## 🎯 **NOTAS IMPORTANTES**

1. **Orden de capturas:** Seguir la secuencia recomendada
2. **Calidad:** Asegurar que el texto sea legible
3. **Contexto:** Incluir URL o comando en cada captura
4. **Completitud:** Verificar que todas las funcionalidades estén visibles
5. **Consistencia:** Usar el mismo navegador y resolución

**El proyecto está 100% funcional y listo para todas las evidencias.**
