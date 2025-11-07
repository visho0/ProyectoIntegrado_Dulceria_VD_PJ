"""
Vistas genéricas para el panel administrativo integrado
Permite CRUD completo de modelos desde el admin-panel sin redirigir al admin de Django
"""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.forms import modelform_factory
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.apps import apps
from .views import get_user_role


def get_model_from_string(app_label, model_name):
    """Obtener un modelo desde su app_label y model_name"""
    try:
        return apps.get_model(app_label, model_name)
    except LookupError:
        return None


def get_model_admin(app_label, model_name):
    """Obtener la configuración del admin para un modelo"""
    model = get_model_from_string(app_label, model_name)
    if model and model in admin.site._registry:
        return admin.site._registry[model]
    return None


def check_permission(request, app_label, model_name, permission_type):
    """Verificar si el usuario tiene un permiso específico"""
    permission = f'{app_label}.{permission_type}_{model_name}'
    return request.user.has_perm(permission)


@login_required
def admin_model_list(request, app_label, model_name):
    """Lista de objetos de un modelo específico"""
    role = get_user_role(request)
    
    # Solo admin y gerente pueden acceder
    if not (request.user.is_staff or role in ['admin', 'manager']):
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('dashboard')
    
    model = get_model_from_string(app_label, model_name)
    if not model:
        messages.error(request, 'Modelo no encontrado.')
        return redirect('admin_panel')
    
    # Verificar permisos
    if not check_permission(request, app_label, model_name, 'view'):
        messages.error(request, 'No tienes permiso para ver este modelo.')
        return redirect('admin_panel')
    
    model_admin = get_model_admin(app_label, model_name)
    
    # Obtener queryset
    queryset = model.objects.all()
    
    # Aplicar filtros del admin si existen
    if model_admin and hasattr(model_admin, 'get_queryset'):
        queryset = model_admin.get_queryset(request)
    
    # Búsqueda
    search_query = request.GET.get('q', '')
    if search_query and model_admin and hasattr(model_admin, 'search_fields'):
        search_fields = model_admin.search_fields
        search_filter = Q()
        for field in search_fields:
            if '__' in field:
                # Campo relacionado
                search_filter |= Q(**{f'{field}__icontains': search_query})
            else:
                search_filter |= Q(**{f'{field}__icontains': search_query})
        queryset = queryset.filter(search_filter)
    
    # Ordenamiento
    ordering = request.GET.get('ordering', '')
    if ordering:
        queryset = queryset.order_by(ordering)
    elif model_admin and hasattr(model_admin, 'ordering'):
        queryset = queryset.order_by(*model_admin.ordering)
    
    # Paginación
    per_page = request.GET.get('per_page', 25)
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Obtener campos para mostrar
    list_display = ['__str__']
    if model_admin and hasattr(model_admin, 'list_display'):
        list_display = model_admin.list_display
    
    # Preparar datos para la tabla
    table_data = []
    for obj in page_obj:
        row = {'obj': obj, 'fields': []}
        for field in list_display:
            if field == '__str__':
                row['fields'].append(str(obj))
            else:
                # Intentar obtener el valor del campo
                try:
                    if '__' in field:
                        # Campo relacionado (ej: 'category__name')
                        parts = field.split('__')
                        value = obj
                        for part in parts:
                            value = getattr(value, part, None)
                            if value is None:
                                break
                        row['fields'].append(str(value) if value is not None else '-')
                    else:
                        # Campo directo
                        value = getattr(obj, field, None)
                        if callable(value):
                            value = value()
                        row['fields'].append(str(value) if value is not None else '-')
                except Exception:
                    row['fields'].append('-')
        table_data.append(row)
    
    context = {
        'model': model,
        'model_name': model._meta.verbose_name_plural,
        'app_label': app_label,
        'model_name_slug': model_name,
        'objects': page_obj,
        'table_data': table_data,
        'list_display': list_display,
        'search_query': search_query,
        'per_page': per_page,
        'has_add_permission': check_permission(request, app_label, model_name, 'add'),
        'has_change_permission': check_permission(request, app_label, model_name, 'change'),
        'has_delete_permission': check_permission(request, app_label, model_name, 'delete'),
    }
    
    return render(request, 'production/admin_model_list.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def admin_model_create(request, app_label, model_name):
    """Crear un nuevo objeto de un modelo"""
    role = get_user_role(request)
    
    # Solo admin y gerente pueden acceder
    if not (request.user.is_staff or role in ['admin', 'manager']):
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('dashboard')
    
    model = get_model_from_string(app_label, model_name)
    if not model:
        messages.error(request, 'Modelo no encontrado.')
        return redirect('admin_panel')
    
    # Verificar permisos
    if not check_permission(request, app_label, model_name, 'add'):
        messages.error(request, 'No tienes permiso para agregar objetos de este modelo.')
        return redirect('admin_panel')
    
    model_admin = get_model_admin(app_label, model_name)
    
    # Crear formulario dinámico
    # Obtener campos editables
    fields = None
    if model_admin and hasattr(model_admin, 'get_fields'):
        fields = model_admin.get_fields(request)
    elif model_admin and hasattr(model_admin, 'fields'):
        fields = model_admin.fields
    
    # Excluir campos readonly
    exclude = []
    if model_admin and hasattr(model_admin, 'readonly_fields'):
        exclude.extend(model_admin.readonly_fields)
    
    # Crear ModelForm
    FormClass = modelform_factory(model, fields=fields, exclude=exclude)
    
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'{model._meta.verbose_name} "{obj}" creado exitosamente.')
            return redirect('admin_model_list', app_label=app_label, model_name=model_name)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = FormClass()
    
    context = {
        'model': model,
        'model_name': model._meta.verbose_name,
        'app_label': app_label,
        'model_name_slug': model_name,
        'form': form,
        'action': 'Crear',
    }
    
    return render(request, 'production/admin_model_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def admin_model_edit(request, app_label, model_name, pk):
    """Editar un objeto existente"""
    role = get_user_role(request)
    
    # Solo admin y gerente pueden acceder
    if not (request.user.is_staff or role in ['admin', 'manager']):
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('dashboard')
    
    model = get_model_from_string(app_label, model_name)
    if not model:
        messages.error(request, 'Modelo no encontrado.')
        return redirect('admin_panel')
    
    # Verificar permisos
    if not check_permission(request, app_label, model_name, 'change'):
        messages.error(request, 'No tienes permiso para editar objetos de este modelo.')
        return redirect('admin_panel')
    
    obj = get_object_or_404(model, pk=pk)
    
    # Verificar permisos específicos del objeto
    model_admin = get_model_admin(app_label, model_name)
    if model_admin and hasattr(model_admin, 'has_change_permission'):
        if not model_admin.has_change_permission(request, obj):
            messages.error(request, 'No tienes permiso para editar este objeto.')
            return redirect('admin_model_list', app_label=app_label, model_name=model_name)
    
    # Crear formulario dinámico
    fields = None
    if model_admin and hasattr(model_admin, 'get_fields'):
        fields = model_admin.get_fields(request, obj)
    elif model_admin and hasattr(model_admin, 'fields'):
        fields = model_admin.fields
    
    # Excluir campos readonly
    exclude = []
    if model_admin and hasattr(model_admin, 'readonly_fields'):
        exclude.extend(model_admin.readonly_fields)
    
    # Crear ModelForm
    FormClass = modelform_factory(model, fields=fields, exclude=exclude)
    
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'{model._meta.verbose_name} "{obj}" actualizado exitosamente.')
            return redirect('admin_model_list', app_label=app_label, model_name=model_name)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = FormClass(instance=obj)
    
    context = {
        'model': model,
        'model_name': model._meta.verbose_name,
        'app_label': app_label,
        'model_name_slug': model_name,
        'form': form,
        'object': obj,
        'action': 'Editar',
    }
    
    return render(request, 'production/admin_model_form.html', context)


@login_required
@require_POST
def admin_model_delete(request, app_label, model_name, pk):
    """Eliminar un objeto"""
    role = get_user_role(request)
    
    # Solo admin y gerente pueden acceder
    if not (request.user.is_staff or role in ['admin', 'manager']):
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('dashboard')
    
    model = get_model_from_string(app_label, model_name)
    if not model:
        messages.error(request, 'Modelo no encontrado.')
        return redirect('admin_panel')
    
    # Verificar permisos
    if not check_permission(request, app_label, model_name, 'delete'):
        messages.error(request, 'No tienes permiso para eliminar objetos de este modelo.')
        return redirect('admin_panel')
    
    obj = get_object_or_404(model, pk=pk)
    
    # Verificar permisos específicos del objeto
    model_admin = get_model_admin(app_label, model_name)
    if model_admin and hasattr(model_admin, 'has_delete_permission'):
        if not model_admin.has_delete_permission(request, obj):
            messages.error(request, 'No tienes permiso para eliminar este objeto.')
            return redirect('admin_model_list', app_label=app_label, model_name=model_name)
    
    obj_name = str(obj)
    obj.delete()
    
    messages.success(request, f'{model._meta.verbose_name} "{obj_name}" eliminado exitosamente.')
    return redirect('admin_model_list', app_label=app_label, model_name=model_name)

