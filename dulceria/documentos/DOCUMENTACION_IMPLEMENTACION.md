# 📋 DOCUMENTACIÓN DETALLADA DE IMPLEMENTACIÓN

## 🎯 RESUMEN EJECUTIVO

Este documento detalla la implementación completa del sistema de gestión de dulcería con:
- ✅ Configuración de sesiones y autenticación
- ✅ Sistema de permisos basado en roles (Admin, Gerente, Empleado, Cliente)
- ✅ CRUD completo de productos con permisos y SweetAlert2
- ✅ Vista de cliente (e-commerce) con carrito de compras
- ✅ Buscador y paginador avanzado
- ✅ Sistema de mensajes flash y contador de visitas

---

## 📁 1. CONFIGURACIÓN DE SESIONES Y AUTENTICACIÓN

### 1.1. Configuración en settings.py

**Archivo:** `dulceria/settings.py`  
**Líneas:** 149-182

```python
# ===========================================
# CONFIGURACIÓN DE SESIONES
# ===========================================

# Duración de la cookie de sesión (en segundos) - 2 horas
SESSION_COOKIE_AGE = 60 * 60 * 2  # 2 horas

# Sesión expira al cerrar el navegador?
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Cada vez que se hace una petición, se actualiza la expiración
SESSION_SAVE_EVERY_REQUEST = False

# Seguridad de las cookies
# En desarrollo: False, en producción con HTTPS: True
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'

# Solo enviar la cookie en el mismo sitio (protección CSRF)
SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')  # 'Lax', 'Strict', o 'None'

# ===========================================
# CONFIGURACIÓN DE MENSAJES (MESSAGE FRAMEWORK)
# ===========================================

from django.contrib.messages import constants as msg

MESSAGE_TAGS = {
    msg.DEBUG: 'secondary',
    msg.INFO: 'info',
    msg.SUCCESS: 'success',
    msg.WARNING: 'warning',
    msg.ERROR: 'danger',  # Bootstrap usa 'danger'
}
```

**Explicación:**
- `SESSION_COOKIE_AGE`: Define que las sesiones expiran después de 2 horas de inactividad
- `SESSION_EXPIRE_AT_BROWSER_CLOSE`: False significa que la sesión persiste al cerrar el navegador
- `SESSION_SAVE_EVERY_REQUEST`: False optimiza el rendimiento al no actualizar en cada petición
- `SESSION_COOKIE_SECURE`: Configurable desde .env para producción con HTTPS
- `SESSION_COOKIE_SAMESITE`: Protege contra ataques CSRF
- `MESSAGE_TAGS`: Mapea los tipos de mensajes de Django a clases de Bootstrap

### 1.2. Vista de Logout Personalizada

**Archivo:** `accounts/views.py`  
**Líneas:** 45-59

```python
def logout_view(request):
    """Vista de logout personalizada que limpia datos de sesión"""
    # 1) Limpiar datos específicos de la sesión
    for key in ("carrito", "filtros_busqueda", "onboarding_step"):
        request.session.pop(key, None)
    
    # 2) Borrar cookies propias si las usaste
    response = redirect("login")
    
    # 3) Ahora cerrar sesión
    from django.contrib.auth import logout
    logout(request)
    
    # Importante: agrega el mensaje DESPUÉS de logout (se crea una nueva sesión vacía)
    messages.info(request, "Sesión cerrada y datos temporales limpiados.")
    
    # Regenerar clave de sesión para mayor seguridad
    request.session.cycle_key()
    
    return response
```

**Explicación:**
- Limpia datos específicos de la sesión (carrito, filtros, etc.)
- Cierra la sesión del usuario
- Regenera la clave de sesión con `cycle_key()` para mayor seguridad
- Muestra mensaje de confirmación

### 1.3. Regeneración de Clave de Sesión en Login

**Archivo:** `accounts/views.py`  
**Líneas:** 18-42

```python
def get_success_url(self):
    # Redirigir según el rol del usuario
    user = self.request.user
    
    if hasattr(user, 'userprofile'):
        role = user.userprofile.role
        # ... redirección según rol ...
        # Regenerar clave de sesión tras login para mayor seguridad
        self.request.session.cycle_key()
```

**Explicación:**
- Después de un login exitoso, se regenera la clave de sesión para prevenir ataques de fijación de sesión

### 1.4. Contador de Visitante en Sesión

**Archivo:** `production/views.py`  
**Líneas:** 23-26 (dashboard), 162-164 (tienda_online)

```python
# Contador de visitas en sesión
visitas = request.session.get('visitas', 0)
request.session['visitas'] = visitas + 1
```

**Explicación:**
- Guarda un contador de visitas en la sesión del usuario
- Se incrementa cada vez que el usuario visita el dashboard o la tienda
- Se muestra en el contexto para visualización

---

## 🔐 2. SISTEMA DE PERMISOS

### 2.1. Permisos en el Modelo Product

**Archivo:** `production/models.py`  
**Líneas:** 31-40

```python
class Meta:
    verbose_name = 'Producto'
    verbose_name_plural = 'Productos'
    ordering = ['name']
    permissions = [
        ('view_product', 'Can view product'),
        ('add_product', 'Can add product'),
        ('change_product', 'Can change product'),
        ('delete_product', 'Can delete product'),
    ]
```

**Explicación:**
- Define permisos personalizados para el modelo Product
- Django crea automáticamente estos permisos al ejecutar migraciones
- Se usan con decoradores `@permission_required` en las vistas

### 2.2. Actualización del Modelo UserProfile

**Archivo:** `accounts/models.py`  
**Líneas:** 50-57

```python
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('employee', 'Empleado'),
        ('viewer', 'Visualizador'),
        ('cliente', 'Cliente'),  # NUEVO: Rol agregado
    ]
```

**Explicación:**
- Se agregó el rol 'cliente' para usuarios externos
- Permite diferenciar entre empleados y clientes en la aplicación

### 2.3. Distribución de Permisos por Rol

**Roles y sus permisos:**

| Rol | Ver Productos | Agregar Productos | Editar Productos | Eliminar Productos |
|-----|---------------|-------------------|------------------|-------------------|
| Admin | ✅ | ✅ | ✅ | ✅ |
| Gerente | ✅ | ✅ | ✅ | ✅ |
| Empleado | ✅ | ✅ | ❌ | ❌ |
| Cliente | ✅ (Tienda) | ❌ | ❌ | ❌ |

**Explicación:**
- Los clientes solo pueden ver productos en la tienda online y agregarlos al carrito
- Los empleados pueden ver y agregar productos, pero no editar ni eliminar
- Los gerentes y administradores tienen acceso completo

---

## 🛠️ 3. CRUD COMPLETO DE PRODUCTOS

### 3.1. Listado de Productos (List)

**Archivo:** `production/views.py`  
**Líneas:** 49-104

```python
@login_required
@permission_required('production.view_product', raise_exception=True)
def products_list(request):
    """Lista de productos con búsqueda, paginación y ordenamiento"""
    role = get_user_role(request)
    
    # Si es cliente, redirigir a la tienda online
    if role == 'cliente':
        return redirect('tienda_online')
    
    # Obtener parámetros de búsqueda y ordenamiento
    q = request.GET.get('q', '')
    sort = request.GET.get('sort', 'name')
    
    # Obtener productos
    products = Product.objects.select_related('category').filter(is_active=True)
    
    # Aplicar búsqueda
    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(sku__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q)
        )
    
    # Aplicar ordenamiento
    allowed_sort_fields = ['name', '-name', 'price', '-price', 'stock', '-stock', 'category__name', '-category__name']
    if sort in allowed_sort_fields:
        products = products.order_by(sort)
    else:
        products = products.order_by('name')
    
    # Obtener elementos por página desde sesión
    per_page = get_pagination_per_page(request)
    
    # Paginación
    paginator = Paginator(products, per_page)
    page = request.GET.get('page', 1)
    # ... manejo de paginación ...
```

**Características:**
- ✅ Verificación de permisos con `@permission_required`
- ✅ Redirección de clientes a tienda online
- ✅ Búsqueda por nombre, SKU, descripción y categoría
- ✅ Ordenamiento por múltiples campos
- ✅ Paginación configurable guardada en sesión
- ✅ Optimización con `select_related('category')`

**Archivo:** `production/urls.py`  
**Línea:** 7

```python
path("products/", views.products_list, name="products_list"),
```

**Archivo:** `templates/production/products_list.html`  
**Líneas:** 1-228

Características del template:
- Tabla responsive con Bootstrap
- Búsqueda y filtros en la parte superior
- Botón "Nuevo Producto" condicionado por permiso `{% if perms.production.add_product %}`
- Columnas de acciones condicionadas por permisos
- Integración con SweetAlert2 para confirmaciones de eliminación

### 3.2. Crear Producto (Create)

**Archivo:** `production/views.py`  
**Líneas:** 106-122

```python
@login_required
@permission_required('production.add_product', raise_exception=True)
def product_create(request):
    """Crear nuevo producto"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Producto "{product.name}" creado exitosamente.')
            return redirect('products_list')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Crear Producto'
    }
    
    return render(request, "production/product_form.html", context)
```

**Características:**
- ✅ Verificación de permiso `add_product`
- ✅ Manejo de imágenes con `request.FILES`
- ✅ Mensaje de éxito con el nombre del producto
- ✅ Redirección al listado después de crear

**Archivo:** `production/urls.py`  
**Línea:** 8

```python
path("products/create/", views.product_create, name="product_create"),
```

### 3.3. Editar Producto (Update)

**Archivo:** `production/views.py`  
**Líneas:** 124-142

```python
@login_required
@permission_required('production.change_product', raise_exception=True)
def product_edit(request, pk):
    """Editar producto existente"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Producto "{product.name}" actualizado exitosamente.')
            return redirect('products_list')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'title': 'Editar Producto',
        'product': product
    }
    
    return render(request, "production/product_form.html", context)
```

**Características:**
- ✅ Verificación de permiso `change_product`
- ✅ Uso de `get_object_or_404` para manejo de errores
- ✅ Actualización de imágenes si se proporcionan

**Archivo:** `production/urls.py`  
**Línea:** 9

```python
path("products/edit/<int:pk>/", views.product_edit, name="product_edit"),
```

### 3.4. Eliminar Producto (Delete) con SweetAlert2

**Archivo:** `production/views.py`  
**Líneas:** 144-161

```python
@login_required
@permission_required('production.delete_product', raise_exception=True)
@require_POST
def product_delete_ajax(request, pk):
    """Elimina un producto y responde JSON para que el frontend actualice la UI sin recargar"""
    # Verificar que la petición sea AJAX
    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        return HttpResponseBadRequest("Solo AJAX")
    
    product = get_object_or_404(Product, pk=pk)
    nombre = product.name
    
    # Verificar que el producto se pueda eliminar (opcional: verificar stock, pedidos, etc.)
    product.delete()
    
    return JsonResponse({"ok": True, "message": f"Producto '{nombre}' eliminado exitosamente."})
```

**Características:**
- ✅ Verificación de permiso `delete_product`
- ✅ Solo acepta peticiones POST y AJAX
- ✅ Respuesta JSON para actualización sin recargar página
- ✅ Mensaje personalizado con el nombre del producto

**Archivo:** `production/urls.py`  
**Línea:** 10

```python
path("products/delete/<int:pk>/", views.product_delete_ajax, name="product_delete_ajax"),
```

**Archivo:** `templates/production/products_list.html`  
**Líneas:** 170-228

**Implementación de SweetAlert2:**

```javascript
// Delegación de eventos para botones borrar
document.addEventListener('click', async (ev) => {
  const btn = ev.target.closest('.btn-delete');
  if (!btn) return;

  const row = btn.closest('tr');
  const productId = btn.dataset.id;
  const url = btn.dataset.url;
  const nombre = row.querySelector('.product-name')?.textContent?.trim() || 'el producto';

  const confirm = await Swal.fire({
    title: `¿Eliminar ${nombre}?`,
    text: "Esta acción no se puede deshacer.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
    confirmButtonColor: "#dc3545"
  });

  if (!confirm.isConfirmed) return;

  // Petición AJAX con CSRF token
  const resp = await fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrftoken,
      'X-Requested-With': 'XMLHttpRequest',
      'Accept': 'application/json'
    }
  });

  // Manejo de respuesta y actualización del DOM
  // ...
});
```

**Explicación del CRUD:**
- **Create**: Formulario con validación, manejo de imágenes, mensaje de éxito
- **Read**: Listado con búsqueda, ordenamiento y paginación
- **Update**: Formulario pre-poblado, actualización de imágenes opcional
- **Delete**: Confirmación con SweetAlert2, eliminación AJAX sin recargar página

---

## 🛒 4. VISTA DE CLIENTE (E-COMMERCE) Y CARRITO

### 4.1. Vista de Tienda Online

**Archivo:** `production/views.py`  
**Líneas:** 168-219

```python
def tienda_online(request):
    """Vista principal de la tienda online para clientes"""
    # Contador de visitas en sesión
    visitas = request.session.get('visitas', 0)
    request.session['visitas'] = visitas + 1
    
    # Obtener parámetros de búsqueda y ordenamiento
    q = request.GET.get('q', '')
    sort = request.GET.get('sort', 'name')
    categoria_id = request.GET.get('categoria', '')
    
    # Obtener productos activos disponibles (stock > 0)
    products = Product.objects.select_related('category').filter(is_active=True, stock__gt=0)
    
    # Aplicar búsqueda
    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(sku__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q)
        )
    
    # Filtrar por categoría
    if categoria_id:
        products = products.filter(category_id=categoria_id)
    
    # Aplicar ordenamiento
    allowed_sort_fields = ['name', '-name', 'price', '-price']
    if sort in allowed_sort_fields:
        products = products.order_by(sort)
    else:
        products = products.order_by('name')
    
    # Paginación
    per_page = get_pagination_per_page(request)
    paginator = Paginator(products, per_page)
    page = request.GET.get('page', 1)
    # ... manejo de paginación ...
    
    # Obtener categorías para el filtro
    categorias = Category.objects.all()
    
    context = {
        'products': page_obj,
        'categorias': categorias,
        'q': q,
        'sort': sort,
        'categoria_id': categoria_id,
        'per_page': per_page,
        'per_page_options': [5, 10, 25, 50],
        'visitas': visitas + 1,
    }
    
    return render(request, "production/tienda_online.html", context)
```

**Características:**
- ✅ Solo muestra productos con stock > 0
- ✅ Búsqueda por nombre, SKU, descripción y categoría
- ✅ Filtro por categoría
- ✅ Ordenamiento por nombre o precio
- ✅ Paginación configurable guardada en sesión
- ✅ Contador de visitas

**Archivo:** `production/urls.py`  
**Línea:** 13

```python
path("tienda/", views.tienda_online, name="tienda_online"),
```

**Archivo:** `templates/production/tienda_online.html`  
**Líneas:** 1-154

**Diseño similar a la imagen proporcionada:**
- Grid de productos tipo e-commerce
- Cards con imágenes, nombres y precios
- Botones "Añadir al Carrito" rojos
- Búsqueda y filtros en la parte superior
- Paginación al final

### 4.2. Agregar al Carrito

**Archivo:** `production/views.py`  
**Líneas:** 221-253

```python
@login_required
@require_POST
def add_to_cart(request, product_id):
    """Agregar producto al carrito (sesión)"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Verificar stock
    if product.stock <= 0:
        messages.error(request, f'Stock insuficiente para "{product.name}".')
        return redirect('tienda_online')
    
    # Obtener carrito de la sesión
    carrito = request.session.get('carrito', {})
    
    # Agregar o actualizar producto en el carrito
    if str(product_id) in carrito:
        cantidad_actual = carrito[str(product_id)]['cantidad']
        if cantidad_actual >= product.stock:
            messages.warning(request, f'No hay suficiente stock disponible para "{product.name}".')
            return redirect('tienda_online')
        carrito[str(product_id)]['cantidad'] += 1
    else:
        carrito[str(product_id)] = {
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'cantidad': 1,
            'imagen': product.imagen.url if product.imagen else '',
        }
    
    # Guardar carrito en sesión
    request.session['carrito'] = carrito
    request.session.modified = True  # Marcar como modificado
    
    messages.success(request, f'Producto "{product.name}" agregado al carrito.')
    return redirect('tienda_online')
```

**Características:**
- ✅ Almacena el carrito en la sesión
- ✅ Verifica stock disponible
- ✅ Incrementa cantidad si el producto ya está en el carrito
- ✅ Mensajes flash informativos
- ✅ Marca la sesión como modificada

**Archivo:** `production/urls.py`  
**Línea:** 14

```python
path("tienda/add_to_cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
```

### 4.3. Ver Carrito

**Archivo:** `production/views.py`  
**Líneas:** 255-275

```python
@login_required
def view_cart(request):
    """Ver el carrito de compras"""
    carrito = request.session.get('carrito', {})
    
    # Calcular totales
    items = []
    total = 0
    
    for key, item in carrito.items():
        subtotal = float(item['price']) * item['cantidad']
        items.append({
            'product': Product.objects.get(id=item['id']),
            'cantidad': item['cantidad'],
            'subtotal': subtotal,
        })
        total += subtotal
    
    context = {
        'items': items,
        'total': total,
        'carrito_count': len(items),
    }
    
    return render(request, "production/carrito.html", context)
```

**Características:**
- ✅ Lee el carrito desde la sesión
- ✅ Calcula subtotales y total
- ✅ Obtiene los objetos Product completos para mostrar información detallada

**Archivo:** `production/urls.py`  
**Línea:** 15

```python
path("carrito/", views.view_cart, name="view_cart"),
```

**Archivo:** `templates/production/carrito.html`  
**Líneas:** 1-89

**Características del template:**
- Tabla con productos en el carrito
- Cantidad editable con formulario
- Botones para eliminar productos
- Cálculo y visualización de totales
- Mensaje si el carrito está vacío

### 4.4. Actualizar Cantidad en Carrito

**Archivo:** `production/views.py`  
**Líneas:** 277-301

```python
@login_required
@require_POST
def update_cart_quantity(request, product_id):
    """Actualizar cantidad de un producto en el carrito"""
    try:
        nueva_cantidad = int(request.POST.get('cantidad', 1))
    except ValueError:
        nueva_cantidad = 1
    
    if nueva_cantidad <= 0:
        return remove_from_cart(request, product_id)
    
    product = get_object_or_404(Product, id=product_id)
    
    if nueva_cantidad > product.stock:
        messages.error(request, f'No hay suficiente stock disponible. Stock actual: {product.stock}')
        return redirect('view_cart')
    
    carrito = request.session.get('carrito', {})
    
    if str(product_id) in carrito:
        carrito[str(product_id)]['cantidad'] = nueva_cantidad
        request.session['carrito'] = carrito
        request.session.modified = True
        messages.success(request, f'Cantidad de "{product.name}" actualizada.')
    
    return redirect('view_cart')
```

**Características:**
- ✅ Valida la nueva cantidad
- ✅ Verifica stock disponible
- ✅ Elimina el producto si la cantidad es 0
- ✅ Actualiza la sesión

### 4.5. Eliminar del Carrito

**Archivo:** `production/views.py`  
**Líneas:** 302-315

```python
@login_required
@require_POST
def remove_from_cart(request, product_id):
    """Eliminar producto del carrito"""
    carrito = request.session.get('carrito', {})
    
    if str(product_id) in carrito:
        producto_nombre = carrito[str(product_id)]['name']
        del carrito[str(product_id)]
        request.session['carrito'] = carrito
        request.session.modified = True
        messages.success(request, f'Producto "{producto_nombre}" eliminado del carrito.')
    else:
        messages.error(request, 'El producto no está en el carrito.')
    
    return redirect('view_cart')
```

**Características:**
- ✅ Elimina el producto del diccionario del carrito
- ✅ Actualiza la sesión
- ✅ Mensaje de confirmación

**Archivo:** `production/urls.py`  
**Líneas:** 16-17

```python
path("carrito/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
path("carrito/update/<int:product_id>/", views.update_cart_quantity, name="update_cart_quantity"),
```

---

## 🔍 5. BUSCADOR Y PAGINADOR

### 5.1. Función de Paginación con Sesión

**Archivo:** `production/views.py`  
**Líneas:** 13-26

```python
def get_pagination_per_page(request):
    """Obtener el número de elementos por página desde la sesión o parámetro"""
    # Primero verificar si viene como parámetro
    per_page = request.GET.get('per_page')
    if per_page:
        # Guardar en sesión
        request.session['per_page'] = int(per_page)
        return int(per_page)
    # Si no, obtener de sesión
    return request.session.get('per_page', 10)  # Por defecto 10
```

**Explicación:**
- Lee el parámetro `per_page` de la URL si existe
- Lo guarda en la sesión para persistencia
- Si no existe, lee de la sesión o usa el valor por defecto (10)

### 5.2. Búsqueda con Q Objects

**Archivo:** `production/views.py`  
**Líneas:** 60-68 (products_list), 181-191 (tienda_online)

```python
# Aplicar búsqueda
if q:
    products = products.filter(
        Q(name__icontains=q) |
        Q(sku__icontains=q) |
        Q(description__icontains=q) |
        Q(category__name__icontains=q)
    )
```

**Explicación:**
- Usa `Q` objects de Django para búsquedas complejas
- Busca en nombre, SKU, descripción y nombre de categoría
- Usa `icontains` para búsqueda case-insensitive y parcial

### 5.3. Ordenamiento Dinámico

**Archivo:** `production/views.py`  
**Líneas:** 70-77 (products_list), 193-199 (tienda_online)

```python
# Aplicar ordenamiento
allowed_sort_fields = ['name', '-name', 'price', '-price', 'stock', '-stock', 'category__name', '-category__name']
if sort in allowed_sort_fields:
    products = products.order_by(sort)
else:
    products = products.order_by('name')
```

**Explicación:**
- Lista blanca de campos permitidos para ordenamiento
- El prefijo `-` indica orden descendente
- Validación para prevenir inyección SQL

### 5.4. Paginación con Django Paginator

**Archivo:** `production/views.py`  
**Líneas:** 80-92 (products_list), 202-212 (tienda_online)

```python
# Paginación
paginator = Paginator(products, per_page)
page = request.GET.get('page', 1)

try:
    page_obj = paginator.page(page)
except PageNotAnInteger:
    page_obj = paginator.page(1)
except EmptyPage:
    page_obj = paginator.page(paginator.num_pages)
```

**Explicación:**
- Usa `Paginator` de Django para dividir los resultados
- Maneja errores de página inválida
- Proporciona `page_obj` con métodos como `has_previous`, `has_next`, etc.

### 5.5. Template de Paginación

**Archivo:** `templates/production/products_list.html`  
**Líneas:** 136-162

```django
{% if products.has_other_pages %}
<nav aria-label="Navegación de páginas">
  <ul class="pagination justify-content-center">
    {% if products.has_previous %}
    <li class="page-item">
      <a class="page-link" href="?page={{ products.previous_page_number }}{% if q %}&q={{ q }}{% endif %}{% if sort %}&sort={{ sort }}{% endif %}">Anterior</a>
    </li>
    {% endif %}
    <!-- ... enlaces de páginas ... -->
  </ul>
</nav>
{% endif %}
```

**Características:**
- Mantiene parámetros de búsqueda y ordenamiento en los enlaces
- Botones "Anterior" y "Siguiente"
- Números de página con rango inteligente
- Información de total de productos

---

## 💬 6. SISTEMA DE MENSAJES FLASH

### 6.1. Configuración en base.html

**Archivo:** `templates/base.html`  
**Líneas:** 102-109

```django
{% if messages %}
    <div class="container mt-3">
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        {% endfor %}
    </div>
{% endif %}
```

**Explicación:**
- Itera sobre todos los mensajes flash almacenados
- Usa `message.tags` para determinar la clase de Bootstrap (success, danger, warning, info)
- Incluye botón de cierre automático

### 6.2. Ejemplos de Uso en Vistas

**Archivo:** `production/views.py`

```python
# Éxito
messages.success(request, f'Producto "{product.name}" creado exitosamente.')

# Error
messages.error(request, f'Stock insuficiente para "{product.name}".')

# Advertencia
messages.warning(request, f'No hay suficiente stock disponible para "{product.name}".')

# Información
messages.info(request, "Sesión cerrada y datos temporales limpiados.")
```

**Mapeo de Tags:**
- `success` → `alert-success` (verde)
- `error` → `alert-danger` (rojo)
- `warning` → `alert-warning` (amarillo)
- `info` → `alert-info` (azul)

---

## 🧭 7. NAVEGACIÓN CONDICIONAL

### 7.1. Navegación por Rol en base.html

**Archivo:** `templates/base.html`  
**Líneas:** 20-41

```django
<ul class="navbar-nav me-auto">
    {% if user.is_authenticated %}
        {% if user.userprofile.role == 'cliente' or user.cliente %}
            <li class="nav-item">
                <a class="nav-link" href="{% url 'tienda_online' %}">
                    <i class="bi bi-shop"></i> Tienda Online
                </a>
            </li>
        {% else %}
            <li class="nav-item">
                <a class="nav-link" href="{% url 'dashboard' %}">
                    <i class="bi bi-house"></i> Dashboard
                </a>
            </li>
            {% if perms.production.view_product %}
            <li class="nav-item">
                <a class="nav-link" href="{% url 'products_list' %}">
                    <i class="bi bi-box"></i> Productos
                </a>
            </li>
            {% endif %}
        {% endif %}
    {% endif %}
</ul>
```

**Explicación:**
- Clientes ven enlace a "Tienda Online"
- Empleados y administradores ven "Dashboard" y "Productos"
- Los enlaces se muestran solo si el usuario tiene los permisos necesarios

### 7.2. Icono de Carrito para Clientes

**Archivo:** `templates/base.html`  
**Líneas:** 46-57

```django
{% if user.userprofile.role == 'cliente' or user.cliente %}
    <!-- Carrito para clientes -->
    <li class="nav-item">
        <a class="nav-link position-relative" href="{% url 'view_cart' %}">
            <i class="bi bi-cart"></i> Carrito
            {% if request.session.carrito %}
                <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                    {{ request.session.carrito|length }}
                </span>
            {% endif %}
        </a>
    </li>
{% endif %}
```

**Explicación:**
- Solo visible para clientes
- Muestra badge con cantidad de productos en el carrito
- Badge rojo cuando hay productos

---

## 📊 RESUMEN DE ARCHIVOS MODIFICADOS/CREADOS

### Archivos de Configuración:
1. **`dulceria/settings.py`** - Configuración de sesiones y mensajes (líneas 149-182)
2. **`.env`** - Variables de entorno para sesiones (creado)

### Archivos de Modelos:
3. **`accounts/models.py`** - Agregado rol 'cliente' (línea 56)
4. **`production/models.py`** - Permisos personalizados (líneas 35-40)

### Archivos de Vistas:
5. **`accounts/views.py`** - Logout personalizado y ciclo de sesión (líneas 45-59, 18-42)
6. **`production/views.py`** - CRUD completo, tienda online, carrito (completo - 301 líneas)

### Archivos de URLs:
7. **`accounts/urls.py`** - Logout personalizado (línea 6)
8. **`production/urls.py`** - Rutas CRUD y carrito (líneas 5-17)

### Archivos de Templates:
9. **`templates/base.html`** - Navegación condicional y mensajes (líneas 20-109)
10. **`templates/production/products_list.html`** - CRUD con permisos y SweetAlert2 (228 líneas)
11. **`templates/production/tienda_online.html`** - Vista e-commerce (154 líneas)
12. **`templates/production/carrito.html`** - Vista de carrito (89 líneas)

---

## ✅ CHECKLIST DE REQUISITOS

- [x] Contador de visitas en sesión
- [x] Carrito simple y/o Campana de Mensaje (agregar/quitar/listar)
- [x] Mensajes flash funcionando
- [x] Ajustar SESSION_COOKIE_AGE y Secure/SameSite
- [x] Usar cycle_key en login crítico
- [x] CRUD completo con permisos
- [x] SweetAlert2 para confirmaciones
- [x] Buscador y paginador
- [x] Vista de cliente (e-commerce)
- [x] Sistema de permisos por rol

---

## 🚀 INSTRUCCIONES PARA USAR

### 1. Ejecutar Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

Esto creará los permisos personalizados definidos en el modelo Product.

### 2. Asignar Permisos a Usuarios

Para asignar permisos a roles específicos, puedes:

**Opción A: Desde el Admin de Django**
1. Ir a `/admin/auth/group/`
2. Crear o editar grupos (Admin, Gerente, Empleado)
3. Asignar permisos `production.view_product`, `production.add_product`, etc.

**Opción B: Desde código**
```python
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from production.models import Product

# Obtener permisos
content_type = ContentType.objects.get_for_model(Product)
permissions = Permission.objects.filter(content_type=content_type)

# Asignar a grupo
admin_group = Group.objects.get(name='Admin')
admin_group.permissions.add(*permissions)
```

### 3. Probar el Sistema

1. **Login como Admin**: Ver todos los productos, crear, editar, eliminar
2. **Login como Gerente**: Mismos permisos que admin
3. **Login como Empleado**: Solo ver y agregar productos
4. **Login como Cliente**: Ver tienda online y agregar al carrito

---

## 📝 NOTAS FINALES

- Todos los permisos están definidos en el modelo Product
- El carrito se almacena en la sesión del usuario
- La paginación se guarda en la sesión para persistencia
- Los mensajes flash se muestran automáticamente en base.html
- SweetAlert2 mejora la UX en las confirmaciones de eliminación
- La navegación se adapta automáticamente según el rol del usuario

**Fecha de creación:** Enero 2025  
**Versión:** 1.0

---

## 🆕 8. ACTUALIZACIONES Y MEJORAS (Versión 2.0)

### 8.1. Módulo de Proveedores

**Archivo:** `production/models.py`  
**Líneas:** 114-172

Se creó el modelo `Proveedor` con los siguientes campos:

```python
class Proveedor(models.Model):
    # Identificación
    rut = models.CharField(max_length=12, validators=[validate_rut_chileno], unique=True)
    razon_social = models.CharField(max_length=200)
    nombre_fantasia = models.CharField(max_length=200, blank=True)
    
    # Datos de contacto
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100)
    pais = models.CharField(max_length=100, default='Chile')
    
    # Condiciones comerciales
    plazo_pago = models.PositiveIntegerField(default=30)
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES, default='CLP')
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Relación con productos
    es_preferente = models.BooleanField(default=False)
```

**Modelo de Relación Producto-Proveedor:**

```python
class ProductoProveedor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    lead_time = models.PositiveIntegerField(default=0)
    es_preferente = models.BooleanField(default=False)
```

**Características:**
- ✅ Gestión completa de información de proveedores
- ✅ Condiciones comerciales (plazos de pago, moneda, descuentos)
- ✅ Relación con productos con costos y lead time
- ✅ Validación de RUT chileno

### 8.2. Actualización del Modelo Product

**Archivo:** `production/models.py`  
**Líneas:** 22-91

Se actualizó el modelo `Product` con todos los campos requeridos:

**Nuevos campos agregados:**
- `marca`: Marca del producto
- `modelo`: Modelo del producto
- `costo_estandar`: Costo estándar del producto
- `costo_promedio`: Costo promedio del producto
- `iva`: Porcentaje de IVA (por defecto 19%)
- `stock_minimo`: Stock mínimo permitido
- `stock_maximo`: Stock máximo permitido
- `punto_reorden`: Punto de reorden
- `es_perecible`: Indica si el producto es perecible
- `control_especial`: Control por lote o serie
- `fecha_vencimiento`: Fecha de vencimiento
- `mes_vencimiento`: Mes de vencimiento (1-12)

**Sistema de SKU Automático:**

```python
def save(self, *args, **kwargs):
    """Generar SKU automáticamente si no existe"""
    if not self.sku:
        # Obtener el último número de SKU
        ultimo_producto = Product.objects.order_by('-id').first()
        if ultimo_producto and ultimo_producto.sku:
            try:
                numero = int(ultimo_producto.sku.replace('SKU-', '').replace('SKU', ''))
            except (ValueError, AttributeError):
                numero = 0
        else:
            numero = 0
        # Generar nuevo SKU
        self.sku = f"SKU-{str(numero + 1).zfill(3)}"
    super().save(*args, **kwargs)
```

**Características:**
- ✅ SKU generado automáticamente con prefijo "SKU-" y numeración secuencial
- ✅ SKU no editable por el usuario
- ✅ Actualización automática de SKU al eliminar productos (mediante señal)

### 8.3. Sistema de Actualización de SKU al Eliminar

**Archivo:** `production/signals.py`  
**Líneas:** 1-18

Se creó una señal para actualizar los SKU cuando se elimina un producto:

```python
@receiver(post_delete, sender=Product)
def actualizar_sku_despues_eliminar(sender, instance, **kwargs):
    """Actualizar los SKU de los productos restantes después de eliminar uno"""
    productos = Product.objects.all().order_by('id')
    
    # Renumerar los SKU
    for index, producto in enumerate(productos, start=1):
        nuevo_sku = f"SKU-{str(index).zfill(3)}"
        if producto.sku != nuevo_sku:
            Product.objects.filter(pk=producto.pk).update(sku=nuevo_sku)
```

**Archivo:** `production/apps.py`  
**Líneas:** 7-9

```python
def ready(self):
    import production.signals  # noqa
```

**Características:**
- ✅ Actualización automática de SKU al eliminar productos
- ✅ Renumeración secuencial de todos los productos restantes

### 8.4. Formulario de Registro Actualizado

**Archivo:** `accounts/forms.py`  
**Líneas:** 118-212

Se creó el formulario `ProveedorRegistrationForm` para registro de proveedores:

**Características:**
- ✅ Validación de RUT (solo números y guión)
- ✅ Validación de máximo de caracteres en todos los campos
- ✅ Campos específicos para proveedores (razón social, nombre de fantasía)

**Archivo:** `accounts/views.py`  
**Líneas:** 139-168

Se actualizó la vista de registro para permitir elegir entre Cliente o Proveedor:

```python
@require_http_methods(["GET", "POST"])
def register_cliente(request):
    """Vista de registro para clientes y proveedores"""
    tipo_registro = request.GET.get('tipo', 'cliente')
    
    if request.method == 'POST':
        tipo_registro = request.POST.get('tipo_registro', 'cliente')
        
        if tipo_registro == 'proveedor':
            form = ProveedorRegistrationForm(request.POST)
        else:
            form = ClienteRegistrationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            # ... mensaje de éxito ...
            return redirect('login')
    else:
        if tipo_registro == 'proveedor':
            form = ProveedorRegistrationForm()
        else:
            form = ClienteRegistrationForm()
    
    return render(request, 'accounts/register_cliente.html', {
        'form': form,
        'tipo_registro': tipo_registro
    })
```

**Archivo:** `templates/accounts/register_cliente.html`  
**Líneas:** 90-100

Se agregó selector de tipo de registro:

```django
<!-- Selector de tipo de registro -->
<div class="mb-4">
    <div class="btn-group w-100" role="group">
        <a href="?tipo=cliente" class="btn {% if tipo_registro == 'cliente' %}btn-primary{% else %}btn-outline-primary{% endif %}">
            <i class="bi bi-person"></i> Cliente
        </a>
        <a href="?tipo=proveedor" class="btn {% if tipo_registro == 'proveedor' %}btn-primary{% else %}btn-outline-primary{% endif %}">
            <i class="bi bi-truck"></i> Proveedor
        </a>
    </div>
</div>
```

**Características:**
- ✅ Selector visual para elegir entre Cliente o Proveedor
- ✅ Formularios dinámicos según el tipo seleccionado
- ✅ Validaciones de máximo de caracteres en todos los campos
- ✅ Validación de RUT (solo números y guión)

### 8.5. Formulario de Productos Actualizado

**Archivo:** `production/forms.py`  
**Líneas:** 6-94

Se actualizó el formulario de productos con todos los nuevos campos y validaciones:

**Nuevos campos en el formulario:**
- Marca, Modelo
- Costo Estándar, Costo Promedio
- IVA (%)
- Stock Mínimo, Stock Máximo, Punto de Reorden
- Producto Perecible (checkbox)
- Control Especial (select: Ninguno, Por Lote, Por Serie)
- Fecha de Vencimiento, Mes de Vencimiento

**Validaciones implementadas:**

```python
def clean(self):
    cleaned_data = super().clean()
    
    # Validar que los valores no sean negativos
    campos_numericos = ['costo_estandar', 'costo_promedio', 'price', 'iva', 
                      'stock', 'stock_minimo', 'stock_maximo', 'punto_reorden']
    
    for campo in campos_numericos:
        valor = cleaned_data.get(campo)
        if valor is not None and valor < 0:
            raise forms.ValidationError({campo: f'El valor no puede ser negativo.'})
    
    # Validar mes de vencimiento
    mes_vencimiento = cleaned_data.get('mes_vencimiento')
    if mes_vencimiento is not None and (mes_vencimiento < 1 or mes_vencimiento > 12):
        raise forms.ValidationError({'mes_vencimiento': 'El mes debe estar entre 1 y 12.'})
    
    # Validar IVA
    iva = cleaned_data.get('iva')
    if iva is not None and (iva < 0 or iva > 100):
        raise forms.ValidationError({'iva': 'El IVA debe estar entre 0 y 100%.'})
    
    return cleaned_data
```

**Características:**
- ✅ SKU no editable (generado automáticamente)
- ✅ Validación de valores no negativos
- ✅ Validación de rangos (IVA 0-100%, mes 1-12)
- ✅ Máximo de caracteres en todos los campos de texto

### 8.6. Mejoras Visuales

**Archivo:** `templates/base.html`  
**Líneas:** 11, 113, 118

**Navbar con color del dashboard:**
```html
<nav class="navbar navbar-expand-lg navbar-dark" style="background-color: #C8102E !important;">
```

**Footer anclado a la base:**
```html
<body style="display: flex; flex-direction: column; min-height: 100vh;">
<main class="container my-4 flex-grow-1">
<footer class="bg-light text-center text-muted py-3 mt-auto" style="margin-top: auto !important;">
```

**Archivo:** `templates/production/products_list.html`  
**Línea:** 93

**Moneda chilena en listado:**
```django
<td>${{ product.price|floatformat:0 }} CLP</td>
```

**Características:**
- ✅ Navbar con color #C8102E (coincide con dashboard)
- ✅ Footer siempre visible en la base de la página
- ✅ Precios mostrados en moneda chilena (CLP)

### 8.7. Eliminación de Dispositivos del Dashboard

**Archivo:** `templates/accounts/dashboard.html`  
**Líneas:** 148-158, 196-227

Se eliminaron las siguientes secciones:
- Tarjeta de estadísticas de "Dispositivos"
- Sección de "Mediciones Recientes"

**Características:**
- ✅ Dashboard más limpio y enfocado en productos
- ✅ Solo muestra estadísticas relevantes (Productos, Categorías)

### 8.8. Vista de Administración Integrada

**Archivo:** `production/views.py`  
**Líneas:** 402-413

Se creó la vista `admin_panel` que redirige al admin de Django:

```python
@login_required
def admin_panel(request):
    """Vista de administración de Django integrada en la página"""
    role = get_user_role(request)
    
    # Solo admin y gerente pueden acceder
    if not (request.user.is_staff or role in ['admin', 'manager']):
        messages.error(request, 'No tienes permiso para acceder a la administración.')
        return redirect('dashboard')
    
    # Redirigir al admin de Django
    return redirect('/admin/')
```

**Archivo:** `production/urls.py`  
**Línea:** 19

```python
path("admin-panel/", views.admin_panel, name="admin_panel"),
```

**Archivo:** `templates/accounts/dashboard.html`  
**Líneas:** 180-186

```django
{% if user_role == 'admin' or user_role == 'manager' %}
<div class="col-md-3 mb-2">
    <a href="{% url 'admin_panel' %}" class="btn btn-outline-danger w-100">
        <i class="bi bi-gear"></i> Administración
    </a>
</div>
{% endif %}
```

**Características:**
- ✅ Acceso a administración desde el dashboard
- ✅ Control de acceso por rol (admin y gerente)
- ✅ Redirección al admin de Django

### 8.9. Modelo ProveedorUser

**Archivo:** `accounts/models.py`  
**Líneas:** 96-113

Se creó el modelo `ProveedorUser` para usuarios proveedores:

```python
class ProveedorUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=12, validators=[validate_rut_chileno])
    razon_social = models.CharField(max_length=200)
    nombre_fantasia = models.CharField(max_length=200, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
```

**Actualización de UserProfile:**
- Se agregó el rol 'proveedor' a `ROLE_CHOICES`

**Características:**
- ✅ Modelo separado para usuarios proveedores
- ✅ Validación de RUT chileno
- ✅ Relación OneToOne con User

### 8.10. Perfil de Usuario con Avatar

**Archivos:**  
- `accounts/models.py` - Campo `avatar` (líneas 52-68)  
- `accounts/forms.py` - Formularios `UserUpdateForm` y `UserProfileForm` (líneas 214-240)  
- `accounts/views.py` - Manejo de actualización de perfil (líneas 125-161)  
- `templates/accounts/profile.html` - Interfaz para subir foto (archivo completo)

**Características:**
- ✅ Nuevo campo `avatar` para almacenar la foto de perfil
- ✅ Formularios para actualizar datos personales y teléfono
- ✅ Vista de perfil permite subir/actualizar la fotografía (con previsualización)
- ✅ Creación automática de `UserProfile` si no existía (compatibilidad con cuentas antiguas)

### 8.11. Rediseño del Formulario de Productos

**Archivos:**  
- `templates/production/product_form.html` - Formulario reorganizado con nuevos campos  
- `production/forms.py` - Campo SKU deshabilitado e informativo (líneas 60-78)

**Mejoras:**
- ✅ Distribución por secciones (identificación, costos, stock, control especial)
- ✅ Nuevos campos visibles: marca, modelo, costos, IVA, stock mínimo/máximo, punto de reorden
- ✅ Campo SKU mostrado como solo lectura con mensaje descriptivo
- ✅ Compatibilidad completa con campos perecibles y fechas de vencimiento

### 8.12. Vista de Categorías en formato Acordeón

**Archivos:**  
- `production/views.py` - Vista `categories_overview` (líneas 198-217)  
- `production/urls.py` - Ruta `categories/` (línea 12)  
- `templates/production/categories.html` - Nueva vista acordeón

**Características:**
- ✅ Acordeón Bootstrap con conteo de productos por categoría
- ✅ Listado de productos activos con precio, stock y SKU
- ✅ Acceso directo para editar productos (según permisos)
- ✅ Enlace rápido desde dashboard y navegación principal

### 8.13. Navegación y Dashboard Actualizados

**Archivos:**  
- `templates/accounts/dashboard.html` - Tarjetas clicables y acceso a categorías  
- `templates/base.html` - Enlace a categorías en la barra de navegación

**Características:**
- ✅ Tarjetas estadísticas enlazadas a vistas (`Productos`, `Categorías`)
- ✅ Acceso rápido a categorías desde acciones del dashboard
- ✅ Navegación consistente con los nuevos módulos

### 8.14. Maestro de Usuarios Ampliado

**Archivos:**  
- `accounts/models.py` - Campos `state`, `mfa_enabled`, `area`, `observaciones`, `sesiones_activas`, `avatar`  
- `accounts/migrations/0006_userprofile_additional_fields.py`  
- `accounts/forms.py` - Formulario de login con “Recordarme”, formularios de perfil y usuario  
- `accounts/views.py` - Helper `ensure_user_profile`, contador de sesiones, formulario editable  
- `templates/accounts/login.html` y `templates/accounts/profile.html`

**Características:**
- ✅ Campo `state` (ACTIVO/BLOQUEADO) y seguimiento de `sesiones_activas`  
- ✅ Bandera `mfa_enabled` (lista para integración TOTP)  
- ✅ Campos de gestión interna (`area`, `observaciones`) editables desde el perfil  
- ✅ Subida de avatar y visualización inmediata  
- ✅ Opción “Recordarme” que extiende la sesión (14 días)  
- ✅ Creación automática y consistente del perfil para cualquier rol (cliente, proveedor, staff)

### 8.15. Maestro de Productos Completo

**Archivos:**  
- `production/models.py` - Campos ampliados y lógica de SKU/punto de reorden  
- `production/migrations/0003_product_extended_fields.py`  
- `production/forms.py`  
- `templates/production/product_form.html`

**Campos agregados o ajustados:**
- Identificación: `ean_upc`, URLs de imagen y ficha técnica  
- Unidades: `uom_compra`, `uom_venta`, `factor_conversion`  
- Precios: `costo_estandar`, `costo_promedio`, `price` ahora opcionales  
- Stock: `stock_maximo`, `punto_reorden` opcionales (se usa stock mínimo por defecto)  
- Control: `control_por_lote`, `control_por_serie`, `es_perecible`  
- Validaciones adicionales (factor > 0, stock máximo ≥ mínimo, IVA 0-100)

**Form UI:** reorganizado en secciones (identificación, unidades, costos, stock, control, documentos) y mensajes claros para SKU automático.

### 8.16. Maestro de Proveedores y Relación Producto-Proveedor

**Archivos:**  
- `production/models.py`  
- `production/migrations/0003_product_extended_fields.py`

**Campos agregados:**
- Contacto comercial: `sitio_web`, `contacto_principal_*`, `condiciones_pago`, `observaciones`, `estado` (ACTIVO/BLOQUEADO)  
- Dirección: `direccion`, `ciudad`, `telefono` ahora opcionales  
- Relación `ProductoProveedor`: `lead_time` (default 7), `min_lote`, `descuento_pct`, validación de preferente único por producto

**Características:**
- ✅ Estructura lista para control detallado de proveedores  
- ✅ Valida RUT único, país por defecto “Chile”, soporta bloqueos  
- ✅ Mantiene un proveedor preferente por producto de forma automática

---

## 📊 RESUMEN DE ARCHIVOS MODIFICADOS/CREADOS (Versión 2.0)

### Archivos Nuevos:
1. **`production/signals.py`** - Señal para actualizar SKU al eliminar productos
2. **`templates/production/categories.html`** - Vista acordeón de categorías
3. **`accounts/migrations/0006_userprofile_additional_fields.py`** - Campos extendidos en perfiles
4. **`production/migrations/0003_product_extended_fields.py`** - Campos extendidos de productos y proveedores

### Archivos de Modelos:
1. **`production/models.py`** - Modelos de proveedores/productos extendidos
2. **`accounts/models.py`** - Perfil de usuario con nuevos atributos y avatar

### Archivos de Formularios:
1. **`accounts/forms.py`** - Formularios de login, registro y perfil actualizados
2. **`production/forms.py`** - ProductForm completo con unidades, URLs y controles

### Archivos de Vistas:
1. **`accounts/views.py`** - Registro cliente/proveedor y actualización de perfil
2. **`production/views.py`** - Vistas `admin_panel` y `categories_overview`

### Archivos de URLs:
1. **`production/urls.py`** - Rutas `admin-panel/` y `categories/`

### Archivos de Templates:
1. **`templates/accounts/register_cliente.html`** - Selector de tipo de registro, validaciones
2. **`templates/accounts/profile.html`** - Formulario editable y foto de perfil
3. **`templates/accounts/dashboard.html`** - Tarjetas y accesos directos actualizados
4. **`templates/base.html`** - Navbar (color, footer fijo, enlace a categorías)
5. **`templates/production/products_list.html`** - Moneda chilena en precios
6. **`templates/production/product_form.html`** - Formulario ampliado y reorganizado

### Archivos de Configuración:
1. **`production/apps.py`** - Registro de señales
2. **`accounts/migrations/0005_userprofile_avatar.py`** - Migración para campo avatar

---

## ✅ CHECKLIST DE REQUISITOS (Versión 2.0)

- [x] Módulo de Proveedores completo
- [x] Registro de cuenta con opciones Cliente o Proveedor
- [x] Modelo Product actualizado con todos los campos requeridos
- [x] Sistema de SKU automático
- [x] Actualización de SKU al eliminar productos
- [x] Validaciones de formularios (máximo de caracteres, RUT solo números, valores no negativos)
- [x] Precios en moneda chilena
- [x] Footer anclado a la base
- [x] Navbar con color del dashboard (#C8102E)
- [x] Vista de administración integrada
- [x] Eliminación de dispositivos del dashboard
- [x] Foto de perfil personalizable
- [x] Vista de categorías en formato acordeón
- [x] Formularios de productos con información completa
- [x] Maestro de usuarios con estado, MFA y observaciones
- [x] Registro de proveedores con información comercial completa
- [x] Relación producto-proveedor con lead time, lote mínimo y descuento
- [x] Formulario de login con opción “Recordarme”

---

**Fecha de actualización:** Enero 2025  
**Versión:** 2.0

