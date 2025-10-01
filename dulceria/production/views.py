from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Avg
from .models import Product, Category, Measurement
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
    user_org = request.user.userprofile.organization
    
    # Obtener productos (en este caso no hay filtro por organización en Product,
    # pero podrías agregarlo si es necesario)
    products = Product.objects.filter(is_active=True).select_related('category')
    
    context = {
        'products': products,
        'user_org': user_org,
    }
    
    return render(request, "production/products_list.html", context)