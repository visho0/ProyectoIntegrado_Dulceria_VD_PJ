# 📋 INSTRUCCIONES PARA MIGRACIÓN Y ACTIVACIÓN DEL SISTEMA DE AUDITORÍA

## ⚠️ ACCIÓN REQUERIDA

Para activar el sistema de auditoría completo, debes ejecutar las siguientes migraciones:

```bash
cd dulceria
python manage.py makemigrations accounts
python manage.py migrate
```

Esto creará la tabla `accounts_auditlog` en la base de datos.

## 🔍 VERIFICAR QUE FUNCIONA

1. **Acceder al Admin de Django:**
   - Ve a `/admin/accounts/auditlog/`
   - Verás una lista vacía inicialmente

2. **Probar la auditoría:**
   - Crea un producto (se registrará automáticamente)
   - Actualiza un producto (se registrará automáticamente)
   - Elimina un producto (se registrará automáticamente)
   - Inicia sesión (se registrará automáticamente)
   - Cierra sesión (se registrará automáticamente)

3. **Ver registros:**
   - Todos los eventos aparecerán en `/admin/accounts/auditlog/`
   - Solo superusuarios pueden eliminar registros
   - Los registros son de solo lectura para todos

## 📝 NOTAS IMPORTANTES

- Los signals se cargan automáticamente cuando Django inicia
- La auditoría funciona automáticamente sin necesidad de código adicional
- Los registros incluyen: usuario, fecha/hora, acción, IP, User Agent, y detalles del objeto

## 🐛 SI HAY PROBLEMAS

Si al ejecutar `makemigrations` no se crea la migración para `AuditLog`:

1. Verifica que `accounts/models_audit.py` existe
2. Verifica que `accounts/admin.py` importa correctamente `AuditLog`
3. Intenta forzar la migración:
   ```bash
   python manage.py makemigrations accounts --empty
   ```
   Luego edita manualmente la migración o contacta al desarrollador.

