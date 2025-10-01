from django.contrib import admin
from .models import Organization, Zone, Device

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'created_at')
    search_fields = ('name', 'organization__name', 'description')
    list_filter = ('organization', 'created_at')
    ordering = ('organization__name', 'name')
    list_select_related = ('organization',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'serial', 'zone', 'organization', 'status', 'created_at')
    search_fields = ('name', 'serial', 'zone__name', 'zone__organization__name')
    list_filter = ('status', 'zone__organization', 'zone', 'created_at')
    ordering = ('zone__organization__name', 'zone__name', 'name')
    list_select_related = ('zone', 'zone__organization')
    readonly_fields = ('created_at', 'updated_at')
    
    def organization(self, obj):
        return obj.zone.organization.name
    organization.short_description = 'Organización'
    organization.admin_order_field = 'zone__organization__name'