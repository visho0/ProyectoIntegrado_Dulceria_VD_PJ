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
    
    # Obtener productos según el rol
    if role == 'proveedor':
        # Proveedores solo ven sus productos
        products = Product.objects.select_related('category').filter(
            is_active=True,
            creado_por=request.user
        )
    else:
        # Admin, manager y empleados ven todos los productos aprobados
        products = Product.objects.select_related('category').filter(
            is_active=True,
            estado_aprobacion='APROBADO'
        )
    
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
    role = get_user_role(request)
    
    # Verificar permiso solo si está asignado, sino permitir acceso
    if not (request.user.is_staff or request.user.has_perm('production.add_product')):
        # Si no tiene permiso explícito pero es staff o tiene perfil, permitir acceso
        if not (hasattr(request.user, 'userprofile') and role in ['admin', 'manager', 'employee', 'proveedor']):
            messages.error(request, 'No tienes permiso para agregar productos.')
            return redirect('products_list')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, user_role=role)
        if form.is_valid():
            product = form.save(commit=False)
            # Si es proveedor, el producto queda pendiente de aprobación
            if role == 'proveedor':
                product.estado_aprobacion = 'PENDIENTE'
                product.creado_por = request.user
            product.save()
            if role == 'proveedor':
                messages.success(request, f'Producto "{product.name}" creado exitosamente. Está pendiente de aprobación por el gerente.')
                return redirect('proveedor_dashboard')
            else:
                messages.success(request, f'Producto "{product.name}" creado exitosamente.')
                return redirect('products_list')
    else:
        form = ProductForm(user_role=role)
    
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
        if role not in ['admin', 'manager', 'proveedor']:
            messages.error(request, 'No tienes permiso para editar productos.')
            return redirect('products_list')
    
    product = get_object_or_404(Product, pk=pk)
    
    # Si es proveedor, solo puede editar sus propios productos
    if role == 'proveedor' and product.creado_por != request.user:
        messages.error(request, 'No tienes permiso para editar este producto.')
        return redirect('proveedor_dashboard')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product, user_role=role)
        if form.is_valid():
            product = form.save()
            if role == 'proveedor':
                # Si el proveedor edita un producto aprobado, vuelve a pendiente
                if product.estado_aprobacion == 'APROBADO':
                    product.estado_aprobacion = 'PENDIENTE'
                    product.save()
                messages.success(request, f'Producto "{product.name}" actualizado exitosamente. Está pendiente de aprobación.')
                return redirect('proveedor_dashboard')
            else:
                messages.success(request, f'Producto "{product.name}" actualizado exitosamente.')
                return redirect('products_list')
    else:
        form = ProductForm(instance=product, user_role=role)
    
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
    
    # Filtrar productos según el rol
    if role == 'proveedor':
        # Proveedores ven sus productos
        products_filter = Product.objects.filter(
            is_active=True,
            creado_por=request.user
        ).order_by('name')
    elif role in ['admin', 'manager', 'employee']:
        # Admin, manager y empleados ven productos aprobados
        products_filter = Product.objects.filter(
            is_active=True,
            estado_aprobacion='APROBADO'
        ).order_by('name')
    else:
        # Clientes ven productos aprobados
        products_filter = Product.objects.filter(
            is_active=True,
            estado_aprobacion='APROBADO'
        ).order_by('name')
    
    categories = Category.objects.all().prefetch_related(
        Prefetch(
            'product_set',
            queryset=products_filter,
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
    
    # Obtener productos activos disponibles (stock > 0) y aprobados
    products = Product.objects.select_related('category').filter(
        is_active=True,
        stock__gt=0,
        estado_aprobacion='APROBADO'
    )
    
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
    from django.contrib import admin
    from django.apps import apps
    
    role = get_user_role(request)
    
    # Solo admin y gerente pueden acceder
    if not (request.user.is_staff or role in ['admin', 'manager']):
        messages.error(request, 'No tienes permiso para acceder a la administración.')
        return redirect('dashboard')
    
    # Obtener todas las aplicaciones y modelos registrados en el admin
    app_dict = {}
    
    for model, model_admin in admin.site._registry.items():
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        verbose_name_plural = model._meta.verbose_name_plural
        
        # Verificar permisos
        has_view = request.user.has_perm(f'{app_label}.view_{model_name}')
        has_add = request.user.has_perm(f'{app_label}.add_{model_name}')
        has_change = request.user.has_perm(f'{app_label}.change_{model_name}')
        has_delete = request.user.has_perm(f'{app_label}.delete_{model_name}')
        
        if has_view or has_add or has_change or has_delete:
            if app_label not in app_dict:
                try:
                    app_config = apps.get_app_config(app_label)
                    app_verbose_name = app_config.verbose_name
                except:
                    app_verbose_name = app_label
                
                app_dict[app_label] = {
                    'name': app_label,
                    'verbose_name': app_verbose_name,
                    'models': []
                }
            
            app_dict[app_label]['models'].append({
                'name': verbose_name_plural,
                'model_name': model_name,
                'app_label': app_label,
                'admin_url': f'/admin-panel/{app_label}/{model_name}/',
                'add_url': f'/admin-panel/{app_label}/{model_name}/add/',
                'has_view': has_view,
                'has_add': has_add,
                'has_change': has_change,
                'has_delete': has_delete,
            })
    
    # Convertir dict a lista ordenada
    app_list = list(app_dict.values())
    app_list.sort(key=lambda x: x['verbose_name'])
    
    context = {
        'app_list': app_list,
        'user_role': role,
    }
    
    return render(request, "production/admin_panel.html", context)


@login_required
def proveedor_dashboard(request):
    """Dashboard del proveedor para modificar datos y gestionar productos"""
    from accounts.models import ProveedorUser
    from accounts.forms import ProveedorUserForm, UserUpdateForm, UserProfileForm
    from accounts.views import ensure_user_profile
    
    role = get_user_role(request)
    
    # Solo proveedores pueden acceder
    if role != 'proveedor':
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('dashboard')
    
    user_profile = ensure_user_profile(request.user)
    
    # Obtener o crear ProveedorUser
    try:
        proveedor_user = ProveedorUser.objects.get(user=request.user)
    except ProveedorUser.DoesNotExist:
        messages.error(request, 'No se encontró tu perfil de proveedor. Contacta al administrador.')
        return redirect('dashboard')
    
    # Obtener productos del proveedor
    mis_productos = Product.objects.filter(creado_por=request.user).order_by('-created_at')
    productos_pendientes = mis_productos.filter(estado_aprobacion='PENDIENTE').count()
    productos_aprobados = mis_productos.filter(estado_aprobacion='APROBADO').count()
    productos_rechazados = mis_productos.filter(estado_aprobacion='RECHAZADO').count()
    
    # Manejar formularios
    if request.method == 'POST':
        if 'update_proveedor' in request.POST:
            proveedor_form = ProveedorUserForm(request.POST, instance=proveedor_user)
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            
            if proveedor_form.is_valid() and user_form.is_valid() and profile_form.is_valid():
                proveedor_form.save()
                user_form.save()
                profile_form.save()
                messages.success(request, 'Tus datos se actualizaron correctamente.')
                return redirect('proveedor_dashboard')
            else:
                messages.error(request, 'Por favor corrige los errores en el formulario.')
        else:
            proveedor_form = ProveedorUserForm(instance=proveedor_user)
            user_form = UserUpdateForm(instance=request.user)
            profile_form = UserProfileForm(instance=user_profile)
    else:
        proveedor_form = ProveedorUserForm(instance=proveedor_user)
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    
    context = {
        'proveedor_user': proveedor_user,
        'proveedor_form': proveedor_form,
        'user_form': user_form,
        'profile_form': profile_form,
        'mis_productos': mis_productos[:10],  # Últimos 10 productos
        'productos_pendientes': productos_pendientes,
        'productos_aprobados': productos_aprobados,
        'productos_rechazados': productos_rechazados,
        'user_profile': user_profile,
    }
    
    return render(request, "production/proveedor_dashboard.html", context)


@login_required
def aprobar_productos(request):
    """Vista para que el gerente apruebe o rechace productos"""
    role = get_user_role(request)
    
    # Solo gerente y admin pueden acceder
    if role not in ['manager', 'admin']:
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('dashboard')
    
    # Obtener productos pendientes
    productos_pendientes = Product.objects.filter(
        estado_aprobacion='PENDIENTE'
    ).select_related('category', 'creado_por').order_by('-created_at')
    
    # Manejar aprobación/rechazo
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        accion = request.POST.get('accion')  # 'aprobar' o 'rechazar'
        
        try:
            producto = Product.objects.get(pk=producto_id, estado_aprobacion='PENDIENTE')
            if accion == 'aprobar':
                from django.utils import timezone
                producto.estado_aprobacion = 'APROBADO'
                producto.aprobado_por = request.user
                producto.fecha_aprobacion = timezone.now()
                producto.save()
                messages.success(request, f'Producto "{producto.name}" aprobado exitosamente.')
            elif accion == 'rechazar':
                producto.estado_aprobacion = 'RECHAZADO'
                producto.aprobado_por = request.user
                producto.save()
                messages.success(request, f'Producto "{producto.name}" rechazado.')
            else:
                messages.error(request, 'Acción no válida.')
        except Product.DoesNotExist:
            messages.error(request, 'Producto no encontrado o ya fue procesado.')
        
        return redirect('aprobar_productos')
    
    context = {
        'productos_pendientes': productos_pendientes,
        'user_role': role,
    }
    
    return render(request, "production/aprobar_productos.html", context)
