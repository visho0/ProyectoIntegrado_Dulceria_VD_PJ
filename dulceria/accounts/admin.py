from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Cliente

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_organization', 'get_role')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'userprofile__organization', 'userprofile__role')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'userprofile__organization__name')
    ordering = ('username',)
    
    def get_queryset(self, request):
        """Filtrar usuarios según el rol del usuario actual"""
        qs = super().get_queryset(request)
        
        # Si es superusuario o admin, puede ver todos
        if request.user.is_superuser:
            return qs
        
        # Si es gerente, solo ve usuarios de su organización
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'manager':
            return qs.filter(userprofile__organization=request.user.userprofile.organization)
        
        return qs.none()  # Otros usuarios no pueden ver nada
    
    def has_add_permission(self, request):
        """Gerentes pueden agregar usuarios"""
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role in ['admin', 'manager']:
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        """Gerentes pueden editar usuarios de su organización"""
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'userprofile'):
            user_role = request.user.userprofile.role
            if user_role == 'admin':
                return True
            if user_role == 'manager':
                if obj is None:
                    return True
                # Solo puede editar usuarios de su organización
                if hasattr(obj, 'userprofile'):
                    return obj.userprofile.organization == request.user.userprofile.organization
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo admin puede eliminar usuarios"""
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin':
            return True
        return False
    
    def get_organization(self, obj):
        try:
            return obj.userprofile.organization.name
        except UserProfile.DoesNotExist:
            return "Sin organización"
    get_organization.short_description = 'Organización'
    get_organization.admin_order_field = 'userprofile__organization__name'
    
    def get_role(self, obj):
        try:
            return obj.userprofile.get_role_display()
        except UserProfile.DoesNotExist:
            return "Sin rol"
    get_role.short_description = 'Rol'
    get_role.admin_order_field = 'userprofile__role'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'phone', 'created_at')
    search_fields = ('user__username', 'user__email', 'organization__name', 'role', 'phone')
    list_filter = ('organization', 'role', 'created_at')
    ordering = ('user__username',)
    list_select_related = ('user', 'organization')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('user', 'rut', 'first_name', 'last_name', 'email', 'phone', 'created_at')
    search_fields = ('user__username', 'rut', 'first_name', 'last_name', 'email', 'phone')
    list_filter = ('created_at',)
    ordering = ('last_name', 'first_name')
    list_select_related = ('user',)
    readonly_fields = ('created_at', 'updated_at')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)