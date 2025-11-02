from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import UserProfile
from .forms import ClienteRegistrationForm


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # Redirigir según el rol del usuario
        user = self.request.user
        
        if hasattr(user, 'userprofile'):
            role = user.userprofile.role
            if role == 'admin':
                # Regenerar clave de sesión tras login para mayor seguridad
                self.request.session.cycle_key()
                return reverse_lazy('dashboard')
            elif role == 'manager':
                self.request.session.cycle_key()
                return reverse_lazy('dashboard')
            elif role == 'cliente':
                self.request.session.cycle_key()
                return reverse_lazy('tienda_online')
            else:  # employee o viewer
                self.request.session.cycle_key()
                return reverse_lazy('products_list')
        elif hasattr(user, 'cliente'):
            # Si es un cliente, redirigir a tienda online
            self.request.session.cycle_key()
            return reverse_lazy('tienda_online')
        
        return reverse_lazy('dashboard')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')


def logout_view(request):
    """Vista de logout personalizada que limpia datos de sesión"""
    # 1) Limpiar datos específicos de la sesión
    for key in ("carrito", "filtros_busqueda", "onboarding_step"):
        request.session.pop(key, None)
    
    # 2) Borrar cookies propias si las usaste
    response = redirect("login")
    # response.delete_cookie("remember_section", samesite="Lax")  # si la definiste antes
    
    # 3) Ahora cerrar sesión
    from django.contrib.auth import logout
    logout(request)
    
    # Importante: agrega el mensaje DESPUÉS de logout (se crea una nueva sesión vacía)
    messages.info(request, "Sesión cerrada y datos temporales limpiados.")
    
    # Regenerar clave de sesión para mayor seguridad
    request.session.cycle_key()
    
    return response


@login_required
def dashboard(request):
    """Dashboard principal con estadísticas básicas"""
    # Verificar si el usuario tiene perfil
    if not hasattr(request.user, 'userprofile'):
        messages.error(request, 'Tu usuario no tiene un perfil asignado. Contacta al administrador.')
        return redirect('login')
    
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
        from organizations.models import Organization, Zone
        
        context.update({
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_categories': Category.objects.count(),
            'total_organizations': Organization.objects.count(),
            'total_zones': Zone.objects.count(),
        })
    
    # Gerente puede ver productos y zonas de su organización
    elif role == 'manager':
        from production.models import Product, Category
        from organizations.models import Zone
        
        context.update({
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_categories': Category.objects.count(),
            'total_zones': Zone.objects.filter(organization=user_org).count(),
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


@require_http_methods(["GET", "POST"])
def register_cliente(request):
    """Vista de registro para clientes"""
    if request.method == 'POST':
        form = ClienteRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'¡Bienvenido {user.first_name}! Tu cuenta ha sido creada exitosamente.')
            return redirect('login')
    else:
        form = ClienteRegistrationForm()
    
    return render(request, 'accounts/register_cliente.html', {'form': form})