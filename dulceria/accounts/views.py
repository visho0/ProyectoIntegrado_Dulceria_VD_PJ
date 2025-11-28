from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, Permission
from django.db.models import F, Count
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook
from organizations.models import Organization
from .models import UserProfile
from .admin_forms import AdminUserCreationForm, AdminClienteCreationForm, AdminProveedorCreationForm
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


def _sync_user_group(user, role):
    """Asigna el grupo de permisos acorde al rol y limpia asociaciones previas."""
    role_group_map = {
        'admin': 'admin',
        'manager': 'manager',
        'employee': 'employee',
    }
    role_permissions_map = {
        'admin': [
            ('production', 'add_product'),
            ('production', 'change_product'),
            ('production', 'delete_product'),
            ('production', 'view_product'),
            ('production', 'add_movimientoinventario'),
            ('production', 'change_movimientoinventario'),
            ('production', 'delete_movimientoinventario'),
            ('production', 'view_movimientoinventario'),
        ],
        'manager': [
            ('production', 'add_product'),
            ('production', 'change_product'),
            ('production', 'delete_product'),
            ('production', 'view_product'),
            ('production', 'add_movimientoinventario'),
            ('production', 'change_movimientoinventario'),
            ('production', 'delete_movimientoinventario'),
            ('production', 'view_movimientoinventario'),
        ],
        'employee': [
            ('production', 'view_product'),
            ('production', 'view_movimientoinventario'),
        ],
    }
    target_group_name = role_group_map.get(role)
    relevant_group_names = set(role_group_map.values())

    if target_group_name:
        target_group, _ = Group.objects.get_or_create(name=target_group_name)
        desired_permissions = []
        for app_label, codename in role_permissions_map.get(role, []):
            try:
                perm = Permission.objects.get(content_type__app_label=app_label, codename=codename)
            except Permission.DoesNotExist:
                continue
            desired_permissions.append(perm)
        if desired_permissions:
            current_perm_ids = set(target_group.permissions.values_list('id', flat=True))
            desired_perm_ids = {perm.id for perm in desired_permissions}
            if current_perm_ids != desired_perm_ids:
                target_group.permissions.set(desired_permissions)
        elif target_group.permissions.exists():
            target_group.permissions.clear()
        if not user.groups.filter(pk=target_group.pk).exists():
            user.groups.add(target_group)
    else:
        target_group = None

    # Remover otros grupos exclusivos si el rol cambió
    for group in user.groups.filter(name__in=relevant_group_names):
        if target_group is None or group.name != target_group.name:
            user.groups.remove(group)


def ensure_user_profile(user):
    if hasattr(user, 'userprofile'):
        profile = user.userprofile
        _sync_user_group(user, profile.role)
        return profile

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
    _sync_user_group(user, role)
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

    def dispatch(self, request, *args, **kwargs):
        """Verificar rate limiting antes de procesar el login"""
        from django.core.cache import cache
        from django.utils import timezone
        from django.http import HttpResponseForbidden
        
        if request.method == 'POST':
            # Obtener IP del cliente
            ip_address = self.get_client_ip(request)
            
            # Verificar si la IP está bloqueada
            lock_key = f'login_lock_{ip_address}'
            lock_expiry = cache.get(lock_key)
            if lock_expiry:
                if timezone.now() < lock_expiry:
                    remaining_time = int((lock_expiry - timezone.now()).total_seconds())
                    return HttpResponseForbidden(
                        f"Demasiados intentos fallidos. Por favor, intente nuevamente en {remaining_time} segundos."
                    )
                else:
                    # El bloqueo expiró, eliminarlo
                    cache.delete(lock_key)
                    cache.delete(f'login_attempts_{ip_address}')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_invalid(self, form):
        """Incrementar contador de intentos fallidos"""
        from django.core.cache import cache
        from django.utils import timezone
        
        if self.request.method == 'POST':
            ip_address = self.get_client_ip(self.request)
            cache_key = f'login_attempts_{ip_address}'
            lock_key = f'login_lock_{ip_address}'
            
            # Solo incrementar si no está bloqueado
            if not cache.get(lock_key):
                attempts = cache.get(cache_key, 0) + 1
                # Guardar intentos por 30 minutos
                cache.set(cache_key, attempts, timeout=1800)
                
                if attempts >= 5:
                    # Bloquear por 15 minutos
                    lock_expiry = timezone.now() + timezone.timedelta(minutes=15)
                    cache.set(lock_key, lock_expiry, timeout=900)
        
        return super().form_invalid(form)
    
    def get_client_ip(self, request):
        """Obtener la IP real del cliente considerando proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip

    def form_valid(self, form):
        from django.core.cache import cache
        from .models_audit import AuditLog
        from django.contrib import messages
        
        # Django ya verifica is_active automáticamente en el backend de autenticación
        # Pero verificamos aquí también para mostrar mensaje personalizado
        
        response = super().form_valid(form)
        
        # Después de autenticación exitosa, verificar estado del perfil
        user = self.request.user
        profile = ensure_user_profile(user)
        
        # Verificar si el usuario está activo (por si acaso Django no lo hizo)
        if not user.is_active:
            from django.contrib.auth import logout
            logout(self.request)
            messages.error(
                self.request,
                'Tu cuenta está inactiva. Por favor, contacta al administrador.'
            )
            return redirect('login')
        
        # Verificar si el perfil tiene estado ACTIVO
        if profile and profile.state != 'ACTIVO':
            from django.contrib.auth import logout
            logout(self.request)
            messages.error(
                self.request,
                'Tu cuenta está bloqueada. Por favor, contacta al administrador.'
            )
            return redirect('login')
        
        # Si todo está bien, continuar con el proceso normal
        if profile:
            UserProfile.objects.filter(pk=profile.pk).update(sesiones_activas=F('sesiones_activas') + 1)
        
        # Limpiar contadores de rate limiting en login exitoso
        ip_address = self.get_client_ip(self.request)
        cache.delete(f'login_attempts_{ip_address}')
        cache.delete(f'login_lock_{ip_address}')
        
        # Registrar evento de login en auditoría
        try:
            AuditLog.registrar(
                request=self.request,
                accion='LOGIN',
                modelo='User',
                objeto=self.request.user,
                descripcion=f'Usuario "{self.request.user.username}" inició sesión',
                ip_address=ip_address,
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')
            )
        except Exception:
            pass  # No fallar si hay error en auditoría
        
        remember = form.cleaned_data.get('remember_me')
        if remember:
            self.request.session.set_expiry(60 * 60 * 24 * 14)
        else:
            self.request.session.set_expiry(0)
        return response
    
    def get_success_url(self):
        # Verificar si el usuario debe cambiar su contraseña
        user = self.request.user
        profile = ensure_user_profile(user)
        
        if profile and profile.must_change_password:
            # Redirigir a cambio de contraseña obligatorio
            return reverse_lazy('change_password_required')
        
        # Redirigir según el rol del usuario
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
            elif role == 'proveedor':
                self.request.session.cycle_key()
                return reverse_lazy('proveedor_dashboard')
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
    from .models_audit import AuditLog
    
    # Registrar evento de logout en auditoría ANTES de cerrar sesión
    if request.user.is_authenticated:
        try:
            # Obtener IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
            
            AuditLog.registrar(
                request=request,
                accion='LOGOUT',
                modelo='User',
                objeto=request.user,
                descripcion=f'Usuario "{request.user.username}" cerró sesión',
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        except Exception:
            pass  # No fallar si hay error en auditoría
    
    # 1) Limpiar datos específicos de la sesión
    for key in ("carrito", "filtros_busqueda", "onboarding_step"):
        request.session.pop(key, None)
    
    # 2) Ahora cerrar sesión
    from django.contrib.auth import logout
    logout(request)
    
    # 3) Crear respuesta de redirect con headers de seguridad
    response = redirect("login")
    
    # Agregar headers para prevenir acceso con botón Atrás
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    response['X-Content-Type-Options'] = 'nosniff'
    response['X-Frame-Options'] = 'DENY'
    response['X-XSS-Protection'] = '1; mode=block'
    
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
    
    # Caché de conteos para mejorar rendimiento
    from django.core.cache import cache
    from production.models import Product, Category
    from organizations.models import Organization, Zone
    
    # Admin puede ver todo
    if role == 'admin':
        # Cachear conteos por 5 minutos (se actualizan frecuentemente pero no en cada request)
        cache_key_products = 'dashboard_total_products'
        cache_key_categories = 'dashboard_total_categories'
        cache_key_orgs = 'dashboard_total_organizations'
        cache_key_zones = 'dashboard_total_zones'
        
        total_products = cache.get(cache_key_products)
        total_categories = cache.get(cache_key_categories)
        total_organizations = cache.get(cache_key_orgs)
        total_zones = cache.get(cache_key_zones)
        
        if total_products is None:
            total_products = Product.objects.filter(is_active=True).count()
            cache.set(cache_key_products, total_products, 300)  # 5 minutos
        
        if total_categories is None:
            total_categories = Category.objects.count()
            cache.set(cache_key_categories, total_categories, 600)  # 10 minutos (cambia menos)
        
        if total_organizations is None:
            total_organizations = Organization.objects.count()
            cache.set(cache_key_orgs, total_organizations, 600)  # 10 minutos
        
        if total_zones is None:
            total_zones = Zone.objects.count()
            cache.set(cache_key_zones, total_zones, 300)  # 5 minutos
        
        context.update({
            'total_products': total_products,
            'total_categories': total_categories,
            'total_organizations': total_organizations,
            'total_zones': total_zones,
        })
    
    # Gerente puede ver productos y zonas de su organización
    elif role == 'manager':
        cache_key_products = 'dashboard_total_products'
        cache_key_categories = 'dashboard_total_categories'
        cache_key_zones = f'dashboard_total_zones_{user_org.id if user_org else "none"}'
        
        total_products = cache.get(cache_key_products)
        total_categories = cache.get(cache_key_categories)
        total_zones = cache.get(cache_key_zones)
        
        if total_products is None:
            total_products = Product.objects.filter(is_active=True).count()
            cache.set(cache_key_products, total_products, 300)
        
        if total_categories is None:
            total_categories = Category.objects.count()
            cache.set(cache_key_categories, total_categories, 600)
        
        if total_zones is None:
            total_zones = Zone.objects.filter(organization=user_org).count() if user_org else 0
            cache.set(cache_key_zones, total_zones, 300)
        
        context.update({
            'total_products': total_products,
            'total_categories': total_categories,
            'total_zones': total_zones,
        })
    
    # Empleado solo puede ver productos
    else:  # employee o viewer
        cache_key_products = 'dashboard_total_products'
        cache_key_categories = 'dashboard_total_categories'
        
        total_products = cache.get(cache_key_products)
        total_categories = cache.get(cache_key_categories)
        
        if total_products is None:
            total_products = Product.objects.filter(is_active=True).count()
            cache.set(cache_key_products, total_products, 300)
        
        if total_categories is None:
            total_categories = Category.objects.count()
            cache.set(cache_key_categories, total_categories, 600)
        
        context.update({
            'total_products': total_products,
            'total_categories': total_categories,
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


@login_required
@require_http_methods(["GET", "POST"])
def create_user_admin(request):
    """Vista para crear usuarios desde el panel de administración (solo admin y gerente)"""
    try:
        # Obtener rol sin import circular
        role = None
        if hasattr(request.user, 'userprofile'):
            role = request.user.userprofile.role
        elif hasattr(request.user, 'cliente'):
            role = 'cliente'
        
        # Solo admin y gerente pueden crear usuarios
        # BODEGA (employee) y CONSULTA (viewer) NO pueden acceder
        if role not in ['admin', 'manager']:
            messages.error(request, 'No tienes permiso para crear usuarios. Solo administradores y gerentes pueden acceder a esta función.')
            return redirect('dashboard')
        
        # Verificar que exista al menos una organización
        if not Organization.objects.exists():
            messages.error(request, 'No hay organizaciones disponibles. Por favor, crea una organización primero.')
            return redirect('admin_panel')
        
        tipo_usuario = request.GET.get('tipo', 'staff')  # Por defecto staff (admin/manager/employee)
        
        if request.method == 'POST':
            tipo_usuario = request.POST.get('tipo_usuario', 'staff')
            
            try:
                if tipo_usuario == 'cliente':
                    form = AdminClienteCreationForm(request.POST)
                elif tipo_usuario == 'proveedor':
                    form = AdminProveedorCreationForm(request.POST)
                else:
                    form = AdminUserCreationForm(request.POST)
                
                if form.is_valid():
                    try:
                        user = form.save(request=request)
                        temporary_password = getattr(user, '_temporary_password', None)
                        tipo_display = {
                            'staff': 'usuario del sistema',
                            'cliente': 'cliente',
                            'proveedor': 'proveedor'
                        }.get(tipo_usuario, 'usuario')
                        
                        # Guardar información para mostrar en SweetAlert2
                        # Necesitamos crear un nuevo formulario vacío para mostrar después del éxito
                        if tipo_usuario == 'cliente':
                            new_form = AdminClienteCreationForm()
                        elif tipo_usuario == 'proveedor':
                            new_form = AdminProveedorCreationForm()
                        else:
                            new_form = AdminUserCreationForm()
                        
                        # Renderizar la misma página con la información del usuario creado
                        return render(request, 'accounts/create_user_admin.html', {
                            'form': new_form,
                            'tipo_usuario': tipo_usuario,
                            'user_created_info': {
                                'username': user.username,
                                'email': user.email,
                                'temporary_password': temporary_password,
                                'tipo': tipo_display
                            },
                            'show_success_alert': True
                        })
                    except Exception as e:
                        import traceback
                        messages.error(request, f'Error al guardar usuario: {str(e)}')
                        # Si hay error, mostrar el formulario con los errores
                        if hasattr(request, 'user') and request.user.is_superuser:
                            messages.error(request, f'Detalles: {traceback.format_exc()}')
                # Si el formulario no es válido, se renderizará con los errores al final
            except Exception as e:
                import traceback
                messages.error(request, f'Error al crear usuario: {str(e)}')
                if hasattr(request, 'user') and request.user.is_superuser:
                    messages.error(request, f'Detalles: {traceback.format_exc()}')
                # Crear un formulario vacío si hay error
                try:
                    if tipo_usuario == 'cliente':
                        form = AdminClienteCreationForm()
                    elif tipo_usuario == 'proveedor':
                        form = AdminProveedorCreationForm()
                    else:
                        form = AdminUserCreationForm()
                except:
                    form = AdminUserCreationForm()
        else:
            try:
                if tipo_usuario == 'cliente':
                    form = AdminClienteCreationForm()
                elif tipo_usuario == 'proveedor':
                    form = AdminProveedorCreationForm()
                else:
                    form = AdminUserCreationForm()
            except Exception as e:
                messages.error(request, f'Error al cargar formulario: {str(e)}')
                return redirect('admin_panel')
        
        return render(request, 'accounts/create_user_admin.html', {
            'form': form,
            'tipo_usuario': tipo_usuario,
            'show_success_alert': False
        })
    except Exception as e:
        import traceback
        messages.error(request, f'Error inesperado: {str(e)}')
        if hasattr(request, 'user') and request.user.is_superuser:
            messages.error(request, f'Detalles del error: {traceback.format_exc()}')
        return redirect('admin_panel')


@login_required
@require_http_methods(["GET"])
def export_users_excel(request):
    """Exportar la información de usuarios y perfiles a Excel"""
    profile = ensure_user_profile(request.user)
    role = profile.role if profile else None

    if role not in ['admin', 'manager']:
        messages.error(request, 'No tienes permiso para exportar usuarios.')
        return redirect('dashboard')

    wb = Workbook()

    # Hoja principal con todos los usuarios
    ws_usuarios = wb.active
    ws_usuarios.title = 'Usuarios'
    ws_usuarios.append([
        'Username', 'Email', 'Nombre', 'Apellido', 'Rol', 'Estado', 'MFA',
        'Organización', 'Teléfono', 'Área/Unidad', 'Observaciones', 'Último acceso'
    ])

    perfiles = UserProfile.objects.select_related('user', 'organization').order_by('role', 'user__username')
    roles_dict = dict(UserProfile.ROLE_CHOICES)

    for perfil in perfiles:
        usuario = perfil.user
        last_login = usuario.last_login
        if last_login and timezone.is_naive(last_login):
            last_login_display = last_login.strftime('%d-%m-%Y %H:%M')
        elif last_login:
            last_login_display = timezone.localtime(last_login).strftime('%d-%m-%Y %H:%M')
        else:
            last_login_display = ''

        ws_usuarios.append([
            usuario.username,
            usuario.email,
            usuario.first_name,
            usuario.last_name,
            roles_dict.get(perfil.role, perfil.role),
            perfil.get_state_display(),
            'Sí' if perfil.mfa_enabled else 'No',
            perfil.organization.name if perfil.organization else '',
            perfil.phone,
            perfil.area,
            perfil.observaciones,
            last_login_display,
        ])

    # Hoja Resumen por Rol
    ws_resumen = wb.create_sheet(title='Resumen por Rol')
    ws_resumen.append(['Rol', 'Descripción', 'Total de usuarios'])

    conteos_qs = UserProfile.objects.values('role').annotate(total=Count('id'))
    conteos = {row['role']: row['total'] for row in conteos_qs}
    for rol_value, rol_label in UserProfile.ROLE_CHOICES:
        total = conteos.get(rol_value, 0)
        ws_resumen.append([rol_value, rol_label, total])

    # Respuesta HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    now = timezone.now()
    if timezone.is_naive(now):
        timestamp = now.strftime('%Y%m%d_%H%M%S')
    else:
        timestamp = timezone.localtime(now).strftime('%Y%m%d_%H%M%S')

    wb.save(response)
    response['Content-Disposition'] = f'attachment; filename="usuarios_{timestamp}.xlsx"'
    return response


@login_required
@require_http_methods(["GET", "POST"])
def change_password_required(request):
    """Vista para cambio de contraseña obligatorio cuando el usuario tiene contraseña temporal"""
    from .forms import RequiredPasswordChangeForm
    from .models import UserProfile
    from django.contrib.auth import logout
    
    profile = ensure_user_profile(request.user)
    
    # Si no debe cambiar la contraseña, redirigir al dashboard
    if not profile or not profile.must_change_password:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RequiredPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            # Actualizar el perfil para indicar que ya cambió la contraseña
            profile.must_change_password = False
            profile.save()
            
            # Cerrar sesión y redirigir al login
            logout(request)
            messages.success(request, 'Tu contraseña ha sido cambiada exitosamente. Por favor, inicia sesión con tu nueva contraseña.')
            return redirect('login')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RequiredPasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password_required.html', {
        'form': form,
        'user': request.user
    })


@login_required
@require_http_methods(["POST"])
def reset_user_password(request, user_id):
    """Vista para que un administrador resetee la contraseña de un usuario"""
    from .utils import generate_temporary_password, send_password_reset_email
    from .models import UserProfile
    from django.contrib.auth.models import User
    
    # Verificar permisos
    role = None
    if hasattr(request.user, 'userprofile'):
        role = request.user.userprofile.role
    
    if role not in ['admin', 'manager']:
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('admin_panel')
    
    try:
        target_user = User.objects.get(pk=user_id)
        profile = ensure_user_profile(target_user)
        
        # Generar nueva contraseña temporal
        temporary_password = generate_temporary_password()
        target_user.set_password(temporary_password)
        target_user.save()
        
        # Marcar que debe cambiar la contraseña
        if profile:
            profile.must_change_password = True
            profile.save()
        
        # Enviar correo
        send_password_reset_email(target_user, temporary_password, request)
        
        messages.success(request, f'Se ha generado una nueva contraseña temporal para el usuario "{target_user.username}". Se ha enviado un correo con las credenciales.')
    except User.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
    except Exception as e:
        messages.error(request, f'Error al resetear contraseña: {str(e)}')
    
    return redirect('admin_panel')


@login_required
@require_http_methods(["GET"])
def user_created_success(request):
    """Vista para mostrar la contraseña generada después de crear un usuario"""
    # Obtener rol sin import circular
    role = None
    if hasattr(request.user, 'userprofile'):
        role = request.user.userprofile.role
    elif hasattr(request.user, 'cliente'):
        role = 'cliente'
    
    # Solo admin y gerente pueden acceder
    if role not in ['admin', 'manager']:
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('dashboard')
    
    # Obtener información de la sesión
    user_info = request.session.get('new_user_created')
    if not user_info:
        messages.info(request, 'No hay información de usuario creado.')
        return redirect('admin_panel')
    
    # Limpiar la sesión
    del request.session['new_user_created']
    
    return render(request, 'accounts/user_created_success.html', {
        'user_info': user_info
    })