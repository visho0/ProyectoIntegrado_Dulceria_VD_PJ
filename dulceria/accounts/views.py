from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from .models import UserProfile


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # Redirigir según el rol del usuario
        user = self.request.user
        if hasattr(user, 'userprofile'):
            role = user.userprofile.role
            if role == 'admin':
                return reverse_lazy('admin:index')
            elif role == 'manager':
                return reverse_lazy('dashboard')
            else:  # employee o viewer
                return reverse_lazy('products_list')
        return reverse_lazy('dashboard')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')


@login_required
def dashboard(request):
    """Dashboard principal con estadísticas básicas"""
    user_profile = request.user.userprofile
    user_org = user_profile.organization
    role = user_profile.role
    
    # Estadísticas básicas según el rol
    context = {
        'user_org': user_org,
        'user_role': role,
        'user_profile': user_profile,
    }
    
    # Admin puede ver todo
    if role == 'admin':
        from production.models import Product, Category
        from organizations.models import Device
        from production.models import Measurement
        
        context.update({
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_categories': Category.objects.count(),
            'total_devices': Device.objects.count(),
            'recent_measurements': Measurement.objects.select_related('device', 'device__zone')[:10],
        })
    
    # Gerente puede ver productos y dispositivos de su organización
    elif role == 'manager':
        from production.models import Product, Category
        from organizations.models import Device
        from production.models import Measurement
        
        context.update({
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_categories': Category.objects.count(),
            'total_devices': Device.objects.filter(zone__organization=user_org).count(),
            'recent_measurements': Measurement.objects.filter(
                device__zone__organization=user_org
            ).select_related('device', 'device__zone')[:10],
        })
    
    # Empleado solo puede ver productos
    else:  # employee o viewer
        from production.models import Product, Category
        
        context.update({
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_categories': Category.objects.count(),
        })
    
    return render(request, "accounts/dashboard.html", context)


@login_required
def profile_view(request):
    """Vista del perfil del usuario"""
    user_profile = request.user.userprofile
    
    context = {
        'user_profile': user_profile,
        'user_org': user_profile.organization,
    }
    
    return render(request, "accounts/profile.html", context)