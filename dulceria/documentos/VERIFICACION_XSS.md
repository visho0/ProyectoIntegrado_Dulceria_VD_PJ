# Verificación de Protección contra XSS Reflejado

## S-VAL-02: Intento de XSS Reflejado

### Objetivo
Verificar que el sistema escapa/sanitiza la salida y no ejecuta JavaScript cuando se ingresa el payload `<script>alert(1)</script>`.

---

## Métodos de Verificación

### 1. Verificación Manual en el Navegador

#### Prueba en Formulario de Recuperación de Contraseña

1. **Acceder al formulario:**
   - Ir a: `http://localhost:8000/password-reset/`

2. **Ingresar payload XSS:**
   - En el campo "Correo Electrónico", ingresar:
     ```
     <script>alert(1)</script>
     ```

3. **Enviar el formulario**

4. **Verificar resultados:**
   - ✓ **CORRECTO**: No debe aparecer un `alert()` en el navegador
   - ✓ **CORRECTO**: El texto debe aparecer como texto plano en la página
   - ✓ **CORRECTO**: En el código fuente HTML (F12 → Elements), debe verse:
     ```html
     &lt;script&gt;alert(1)&lt;/script&gt;
     ```
   - ✗ **INCORRECTO**: Si aparece un `alert()`, hay vulnerabilidad XSS

#### Prueba en Formulario de Login

1. **Acceder al formulario:**
   - Ir a: `http://localhost:8000/accounts/login/`

2. **Ingresar payload XSS:**
   - En el campo "Usuario", ingresar:
     ```
     <script>alert(1)</script>
     ```

3. **Enviar el formulario**

4. **Verificar resultados:**
   - ✓ **CORRECTO**: No debe aparecer un `alert()` en el navegador
   - ✓ **CORRECTO**: El error debe mostrar el texto escapado

---

### 2. Verificación con Script Automatizado

Ejecutar el script de prueba:

```bash
cd dulceria
python manage.py shell < test_xss_reflected.py
```

El script verificará:
- Formulario de recuperación de contraseña
- Formulario de login
- Sistema de mensajes flash

---

### 3. Verificación del Código Fuente

#### Revisar Templates

Django escapa automáticamente las variables en templates cuando se usa `{{ variable }}`.

**Verificar que NO se use `|safe` incorrectamente:**

```bash
# Buscar usos de |safe que puedan ser peligrosos
grep -r "|safe" dulceria/templates/
```

**Ubicaciones críticas a verificar:**

1. **Mensajes de error de formularios:**
   - `templates/accounts/password_reset.html` - línea 70: `{{ error }}`
   - `templates/accounts/login.html` - línea 117: `{{ error }}`
   - ✓ Deben usar `{{ error }}` sin `|safe`

2. **Valores de campos de formulario:**
   - `templates/accounts/login.html` - línea 112: `{{ form.username.value|default:'' }}`
   - ✓ Deben usar `{{ variable }}` sin `|safe`

3. **Mensajes flash:**
   - `templates/base.html` - línea 127: `{{ message }}`
   - ✓ Debe usar `{{ message }}` sin `|safe`

---

## Resultados Esperados

### ✓ Comportamiento Correcto (Protegido)

1. **En el navegador:**
   - No aparece ningún `alert()`
   - El texto se muestra como texto plano: `<script>alert(1)</script>`

2. **En el código fuente HTML:**
   ```html
   &lt;script&gt;alert(1)&lt;/script&gt;
   ```
   Los caracteres `<` y `>` están escapados como `&lt;` y `&gt;`

3. **En la consola del navegador:**
   - No hay errores de JavaScript
   - No se ejecuta código JavaScript

### ✗ Comportamiento Incorrecto (Vulnerable)

1. **En el navegador:**
   - Aparece un `alert(1)` cuando se envía el formulario
   - Se ejecuta código JavaScript

2. **En el código fuente HTML:**
   ```html
   <script>alert(1)</script>
   ```
   Los caracteres NO están escapados

---

## Cómo Django Protege contra XSS

### Escape Automático

Django escapa automáticamente las variables en templates:

```django
{{ variable }}  <!-- Escapado automáticamente -->
```

Esto convierte:
- `<` → `&lt;`
- `>` → `&gt;`
- `"` → `&quot;`
- `'` → `&#x27;`
- `&` → `&amp;`

### Cuando NO Escapar (Usar |safe)

Solo usar `|safe` cuando:
- El contenido es confiable (generado por el sistema, no por el usuario)
- El contenido ya está sanitizado
- Es HTML seguro generado por Django (ej: `mark_safe()`)

**Ejemplo seguro:**
```django
{{ form.as_p }}  <!-- Django genera HTML seguro -->
```

**Ejemplo peligroso:**
```django
{{ user_input|safe }}  <!-- NUNCA hacer esto con input del usuario -->
```

---

## Checklist de Verificación

- [ ] Probar payload `<script>alert(1)</script>` en formulario de recuperación de contraseña
- [ ] Probar payload en formulario de login
- [ ] Verificar que no aparece `alert()` en el navegador
- [ ] Verificar que el código fuente HTML muestra caracteres escapados
- [ ] Revisar que no hay uso incorrecto de `|safe` con input del usuario
- [ ] Verificar mensajes flash con payload XSS
- [ ] Revisar todos los formularios que muestran errores

---

## Reporte de Verificación

**Fecha:** _______________

**Resultado:** 
- [ ] ✓ PASÓ - El sistema escapa correctamente la salida
- [ ] ✗ FALLÓ - Se detectó vulnerabilidad XSS

**Evidencia:**
- [ ] Capturas de pantalla del navegador
- [ ] Captura del código fuente HTML
- [ ] Resultados del script automatizado

**Observaciones:**
_________________________________________________
_________________________________________________

