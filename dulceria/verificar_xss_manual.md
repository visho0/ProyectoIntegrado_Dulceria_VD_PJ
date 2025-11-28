# Guía Rápida: Verificar Protección XSS Reflejado

## Prueba Rápida (5 minutos)

### Paso 1: Probar en Recuperación de Contraseña

1. Abre tu navegador y ve a: `http://localhost:8000/password-reset/`
2. Abre las herramientas de desarrollador (F12)
3. Ve a la pestaña "Console"
4. En el campo "Correo Electrónico", ingresa exactamente:
   ```
   <script>alert(1)</script>
   ```
5. Haz clic en "Enviar Instrucciones"
6. **Verifica:**
   - ✓ NO debe aparecer un popup con "1"
   - ✓ El texto debe verse como texto plano en la página
   - ✓ En la consola NO debe haber errores de JavaScript ejecutado

### Paso 2: Verificar en el Código Fuente

1. Después de enviar el formulario, presiona `Ctrl+U` (o clic derecho → Ver código fuente)
2. Busca el texto que ingresaste (`<script>alert(1)</script>`)
3. **Verifica:**
   - ✓ Debe aparecer como: `&lt;script&gt;alert(1)&lt;/script&gt;`
   - ✗ NO debe aparecer como: `<script>alert(1)</script>`

### Paso 3: Probar en Login

1. Ve a: `http://localhost:8000/accounts/login/`
2. En el campo "Usuario", ingresa:
   ```
   <script>alert(1)</script>
   ```
3. En "Contraseña", ingresa cualquier cosa
4. Haz clic en "Iniciar Sesión"
5. **Verifica:**
   - ✓ NO debe aparecer un popup
   - ✓ El error debe mostrar el texto escapado

## Resultado Esperado

✅ **PASÓ**: Si NO aparece el alert y el texto está escapado en el código fuente
❌ **FALLÓ**: Si aparece el alert o el código se ejecuta

## Nota Importante

Django escapa automáticamente las variables en templates con `{{ }}`, por lo que deberías estar protegido. Esta prueba verifica que funciona correctamente.

