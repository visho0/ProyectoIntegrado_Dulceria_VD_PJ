from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

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

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)