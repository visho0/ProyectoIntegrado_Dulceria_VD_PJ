from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.db.models import F
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from organizations.models import Organization
from .models import UserProfile
def _get_default_organization(preferred_names=None):
    preferred_names = preferred_names or []
    for name in preferred_names:
        org = Organization.objects.filter(name__iexact=name).first()
        if org:
            return org
    org = Organization.objects.filter(name__iexact='Dulcería Central').first()
    if org:
        return org
    org = Organization.objects.first()
    if org:
        return org
    return Organization.objects.create(name='Dulcería Central')


def ensure_user_profile(user):
    if hasattr(user, 'userprofile'):
        return user.userprofile

    if hasattr(user, 'cliente'):
        role = 'cliente'
        preferences = ['Clientes', 'Dulcería Central']
    elif hasattr(user, 'proveedoruser'):
        role = 'proveedor'
        preferences = ['Red de Proveedores', 'Proveedores', 'Dulcería Central']
    elif user.is_staff:
        role = 'employee'
        preferences = ['Dulcería Central']
    else:
        role = 'viewer'
        preferences = ['Dulcería Central']

    organization = _get_default_organization(preferences)
    profile = UserProfile.objects.create(
        user=user,
        organization=organization,
        role=role,
        state='ACTIVO',
        mfa_enabled=False,
        sesiones_activas=0
    )
    return profile


from .forms import (
    LoginForm,
    ClienteRegistrationForm,
    ProveedorRegistrationForm,
    UserProfileForm,
    UserUpdateForm,
)


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    form_class = LoginForm

    def form_valid(self, form):
        response = super().form_valid(form)
        profile = ensure_user_profile(self.request.user)
        if profile:
            UserProfile.objects.filter(pk=profile.pk).update(sesiones_activas=F('sesiones_activas') + 1)
        remember = form.cleaned_data.get('remember_me')
        if remember:
            self.request.session.set_expiry(60 * 60 * 24 * 14)
        else:
            self.request.session.set_expiry(0)
        return response

    def get_success_url(self):
        # Redirigir según el rol del usuario
        user = self.request.user
        profile = ensure_user_profile(user)

        if profile:
            role = profile.role
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
    user_profile = ensure_user_profile(request.user)
    if not user_profile:
        messages.error(request, 'No se pudo crear el perfil de usuario. Contacta al administrador.')
        return redirect('logout')

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
    user_profile = ensure_user_profile(request.user)
    if not user_profile:
        messages.error(request, 'No se pudo cargar tu perfil. Contacta al administrador.')
        return redirect('dashboard')
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Tu perfil se actualizó correctamente.')
            return redirect('profile')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)

    context = {
        'user_profile': user_profile,
        'user_org': user_profile.organization,
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, "accounts/profile.html", context)


@require_http_methods(["GET", "POST"])
def register_cliente(request):
    """Vista de registro para clientes y proveedores"""
    tipo_registro = request.GET.get('tipo', 'cliente')  # Por defecto cliente
    
    if request.method == 'POST':
        tipo_registro = request.POST.get('tipo_registro', 'cliente')
        
        if tipo_registro == 'proveedor':
            form = ProveedorRegistrationForm(request.POST)
        else:
            form = ClienteRegistrationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            if tipo_registro == 'proveedor':
                messages.success(request, f'¡Bienvenido {user.first_name}! Tu cuenta de proveedor ha sido creada exitosamente.')
            else:
                messages.success(request, f'¡Bienvenido {user.first_name}! Tu cuenta ha sido creada exitosamente.')
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