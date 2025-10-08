from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Avg
from .models import Product, Category, Measurement
from .forms import ProductForm
from organizations.models import Organization, Device

@login_required
def dashboard(request):
    """Dashboard principal con estadísticas básicas"""
    user_org = request.user.userprofile.organization
    
    # Estadísticas básicas
    total_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.count()
    total_devices = Device.objects.filter(zone__organization=user_org).count()
    
    # Últimas mediciones
    recent_measurements = Measurement.objects.filter(
        device__zone__organization=user_org
    ).select_related('device', 'device__zone')[:10]
    
    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_devices': total_devices,
        'recent_measurements': recent_measurements,
        'user_org': user_org,
    }
    
    return render(request, "production/dashboard.html", context)

@login_required
def products_list(request):
    """Lista de productos filtrada por organización del usuario"""
    # Verificar si el usuario tiene perfil
    if not hasattr(request.user, 'userprofile'):
        messages.error(request, 'Tu usuario no tiene un perfil asignado. Contacta al administrador.')
        return redirect('login')
    
    user_org = request.user.userprofile.organization
    
    # Obtener productos (en este caso no hay filtro por organización en Product,
    # pero podrías agregarlo si es necesario)
    products = Product.objects.filter(is_active=True).select_related('category')
    
    context = {
        'products': products,
        'user_org': user_org,
    }
    
    return render(request, "production/products_list.html", context)

@login_required
def product_create(request):
    """Crear nuevo producto"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Incluir request.FILES para manejar imágenes
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
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
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)  # Incluir request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('products_list')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'title': 'Editar Producto',
        'product': product
    }
    
    return render(request, "production/product_form.html", context)