from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count, Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Product, Category
from .forms import ProductForm
from organizations.models import Organization, Zone


def get_user_role(request):
    """Obtener el rol del usuario"""
    if hasattr(request.user, 'userprofile'):
        return request.user.userprofile.role
    elif hasattr(request.user, 'cliente'):
        return 'cliente'
    return None


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


@login_required
def dashboard(request):
    """Dashboard principal con estadísticas básicas y contador de visitas"""
    # Contador de visitas en sesión
    visitas = request.session.get('visitas', 0)
    request.session['visitas'] = visitas + 1
    
    role = get_user_role(request)
    
    if not role or role == 'cliente':
        return redirect('tienda_online')
    
    user_org = request.user.userprofile.organization if hasattr(request.user, 'userprofile') else None
    
    # Estadísticas básicas según el rol
    context = {
        'visitas': visitas + 1,
        'user_org': user_org,
        'user_role': role,
    }
    
    # Admin puede ver todo
    if role == 'admin':
        context.update({
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_categories': Category.objects.count(),
            'total_organizations': Organization.objects.count(),
            'total_zones': Zone.objects.count(),
        })
    
    # Gerente puede ver productos y zonas de su organización
    elif role == 'manager':
        context.update({
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_categories': Category.objects.count(),
            'total_zones': Zone.objects.filter(organization=user_org).count(),
        })
    
    # Empleado solo puede ver productos
    else:  # employee o viewer
        context.update({
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_categories': Category.objects.count(),
        })
    
    return render(request, "production/dashboard.html", context)


@login_required
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
    
    # Obtener elementos por página
    per_page = get_pagination_per_page(request)
    
    # Paginación
    paginator = Paginator(products, per_page)
    page = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'products': page_obj,
        'q': q,
        'sort': sort,
        'per_page': per_page,
        'per_page_options': [5, 10, 25, 50],
    }
    
    return render(request, "production/products_list.html", context)


@login_required
def product_create(request):
    """Crear nuevo producto"""
    # Verificar permiso solo si está asignado, sino permitir acceso
    if not (request.user.is_staff or request.user.has_perm('production.add_product')):
        # Si no tiene permiso explícito pero es staff o tiene perfil, permitir acceso
        if not (hasattr(request.user, 'userprofile') and get_user_role(request) in ['admin', 'manager', 'employee']):
            messages.error(request, 'No tienes permiso para agregar productos.')
            return redirect('products_list')
    
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


@login_required
def product_edit(request, pk):
    """Editar producto existente"""
    # Verificar permiso solo si está asignado, sino permitir acceso según rol
    role = get_user_role(request)
    if not (request.user.is_staff or request.user.has_perm('production.change_product')):
        if role not in ['admin', 'manager']:
            messages.error(request, 'No tienes permiso para editar productos.')
            return redirect('products_list')
    
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


@login_required
@require_POST
def product_delete_ajax(request, pk):
    """Elimina un producto y responde JSON para que el frontend actualice la UI sin recargar"""
    # Verificar permiso solo si está asignado, sino permitir acceso según rol
    role = get_user_role(request)
    if not (request.user.is_staff or request.user.has_perm('production.delete_product')):
        if role not in ['admin', 'manager']:
            return JsonResponse({"ok": False, "message": "No tienes permiso para eliminar productos."}, status=403)
    
    # Verificar que la petición sea AJAX
    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        return HttpResponseBadRequest("Solo AJAX")
    
    product = get_object_or_404(Product, pk=pk)
    nombre = product.name
    
    # Verificar que el producto se pueda eliminar (opcional: verificar stock, pedidos, etc.)
    product.delete()
    
    return JsonResponse({"ok": True, "message": f"Producto '{nombre}' eliminado exitosamente."})


# ===========================================
# CATEGORÍAS
# ===========================================


@login_required
def categories_overview(request):
    """Vista de categorías con productos asociados en formato acordeón"""
    role = get_user_role(request)
    categories = Category.objects.all().prefetch_related(
        Prefetch(
            'product_set',
            queryset=Product.objects.filter(is_active=True).order_by('name'),
            to_attr='active_products'
        )
    )

    context = {
        'categories': categories,
        'user_role': role,
    }
    return render(request, "production/categories.html", context)


# ===========================================
# VISTAS PARA CLIENTES (TIENDA ONLINE)
# ===========================================

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
    
    # Obtener elementos por página
    per_page = get_pagination_per_page(request)
    
    # Paginación
    paginator = Paginator(products, per_page)
    page = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
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
