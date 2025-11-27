"""
Vistas genéricas para el panel administrativo integrado
Permite CRUD completo de modelos desde el admin-panel sin redirigir al admin de Django
"""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.forms import modelform_factory, widgets
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from django.db.models import Q, CharField, TextField, IntegerField, DecimalField, DateField, DateTimeField, BooleanField, EmailField, URLField, ForeignKey, ManyToManyField
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


def get_widget_for_field(field):
    """Obtener widget apropiado según el tipo de campo del modelo"""
    # Verificar si es una instancia de campo o una clase
    from django.db import models
    
    # CharField con max_length
    if isinstance(field, (CharField, models.CharField)):
        max_length = field.max_length if hasattr(field, 'max_length') else None
        attrs = {'class': 'form-control'}
        if max_length:
            attrs['maxlength'] = str(max_length)
        return widgets.TextInput(attrs=attrs)
    
    # TextField
    elif isinstance(field, (TextField, models.TextField)):
        attrs = {'class': 'form-control', 'rows': 3}
        # Intentar obtener max_length si existe
        if hasattr(field, 'max_length') and field.max_length:
            attrs['maxlength'] = str(field.max_length)
        return widgets.Textarea(attrs=attrs)
    
    # IntegerField
    elif isinstance(field, (IntegerField, models.IntegerField, models.PositiveIntegerField, models.BigIntegerField)):
        attrs = {'class': 'form-control', 'type': 'number'}
        if hasattr(field, 'validators'):
            for validator in field.validators:
                if hasattr(validator, 'limit_value'):
                    if validator.limit_value >= 0:
                        attrs['min'] = '0'
        return widgets.NumberInput(attrs=attrs)
    
    # DecimalField
    elif isinstance(field, (DecimalField, models.DecimalField)):
        attrs = {'class': 'form-control', 'type': 'number', 'step': '0.01'}
        if hasattr(field, 'validators'):
            for validator in field.validators:
                if hasattr(validator, 'limit_value'):
                    if validator.limit_value >= 0:
                        attrs['min'] = '0'
        return widgets.NumberInput(attrs=attrs)
    
    # DateField
    elif isinstance(field, (DateField, models.DateField)):
        return widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    
    # DateTimeField
    elif isinstance(field, (DateTimeField, models.DateTimeField)):
        return widgets.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    
    # BooleanField
    elif isinstance(field, (BooleanField, models.BooleanField)):
        return widgets.CheckboxInput(attrs={'class': 'form-check-input'})
    
    # EmailField
    elif isinstance(field, (EmailField, models.EmailField)):
        attrs = {'class': 'form-control', 'type': 'email'}
        if hasattr(field, 'max_length') and field.max_length:
            attrs['maxlength'] = str(field.max_length)
        return widgets.EmailInput(attrs=attrs)
    
    # URLField
    elif isinstance(field, (URLField, models.URLField)):
        attrs = {'class': 'form-control', 'type': 'url'}
        if hasattr(field, 'max_length') and field.max_length:
            attrs['maxlength'] = str(field.max_length)
        return widgets.URLInput(attrs=attrs)
    
    # ForeignKey
    elif isinstance(field, (ForeignKey, models.ForeignKey)):
        return widgets.Select(attrs={'class': 'form-control'})
    
    # ManyToManyField
    elif isinstance(field, (ManyToManyField, models.ManyToManyField)):
        return widgets.SelectMultiple(attrs={'class': 'form-control'})
    
    # Por defecto, usar TextInput
    return widgets.TextInput(attrs={'class': 'form-control'})


@login_required
def admin_model_list(request, app_label, model_name):
    """Lista de objetos de un modelo específico"""
    role = get_user_role(request)
    
    # Solo admin y gerente pueden crear objetos desde admin
    # BODEGA (employee) y CONSULTA (viewer) NO pueden acceder
    if role not in ['admin', 'manager'] and not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para crear objetos. Solo administradores y gerentes pueden realizar esta acción.')
        return redirect('admin_panel' if role in ['admin', 'manager'] else 'dashboard')
    
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
    
    # Búsqueda mejorada - funciona incluso sin search_fields definidos
    search_query = request.GET.get('q', '')
    if search_query:
        if model_admin and hasattr(model_admin, 'search_fields'):
            # Usar campos definidos en el admin
            search_fields = model_admin.search_fields
            search_filter = Q()
            for field in search_fields:
                if '__' in field:
                    search_filter |= Q(**{f'{field}__icontains': search_query})
                else:
                    search_filter |= Q(**{f'{field}__icontains': search_query})
            queryset = queryset.filter(search_filter)
        else:
            # Búsqueda genérica en campos comunes
            search_filter = Q()
            # Buscar en campos comunes de texto
            text_fields = ['name', 'nombre', 'title', 'titulo', 'description', 'descripcion', 
                          'email', 'username', 'sku', 'codigo', 'rut']
            for field_name in text_fields:
                try:
                    field = model._meta.get_field(field_name)
                    if isinstance(field, (CharField, TextField, EmailField)):
                        search_filter |= Q(**{f'{field_name}__icontains': search_query})
                except:
                    pass
            # También buscar en __str__
            if search_filter:
                queryset = queryset.filter(search_filter)
    
    # Optimizar consultas con select_related y prefetch_related cuando sea posible
    # Esto mejora el rendimiento con grandes volúmenes de datos
    try:
        # Intentar detectar ForeignKey automáticamente
        related_fields = [f.name for f in model._meta.get_fields() 
                         if isinstance(f, ForeignKey)]
        if related_fields:
            queryset = queryset.select_related(*related_fields[:5])  # Limitar a 5 para evitar problemas
    except:
        pass
    
    # Ordenamiento
    ordering = request.GET.get('ordering', '')
    if ordering:
        queryset = queryset.order_by(ordering)
    elif model_admin and hasattr(model_admin, 'ordering'):
        queryset = queryset.order_by(*model_admin.ordering)
    else:
        # Ordenamiento por defecto: por id descendente (más recientes primero)
        queryset = queryset.order_by('-id')
    
    # Paginación optimizada - permitir valores más altos para pruebas de stress
    per_page = int(request.GET.get('per_page', 25))
    # Limitar per_page a valores razonables pero permitir pruebas de stress
    if per_page > 500:
        per_page = 500
    elif per_page < 10:
        per_page = 10
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
    from django.contrib.auth.models import User
    
    role = get_user_role(request)
    
    # Solo admin y gerente pueden crear objetos desde admin
    # BODEGA (employee) y CONSULTA (viewer) NO pueden acceder
    if role not in ['admin', 'manager'] and not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para crear objetos. Solo administradores y gerentes pueden realizar esta acción.')
        return redirect('admin_panel' if role in ['admin', 'manager'] else 'dashboard')
    
    model = get_model_from_string(app_label, model_name)
    if not model:
        messages.error(request, 'Modelo no encontrado.')
        return redirect('admin_panel')
    
    # Caso especial: redirigir creación de usuarios a la vista personalizada
    if model == User and app_label == 'auth':
        # Redirigir directamente a la URL de creación de usuarios
        return redirect('/accounts/admin/crear-usuario/')
    
    # Bloquear creación de proveedores desde admin - deben registrarse desde autenticación
    if app_label == 'production' and model_name.lower() == 'proveedor':
        messages.error(request, 'Los proveedores deben registrarse desde la página de autenticación y verificación. No se pueden crear desde el panel de administración.')
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
    
    # Crear diccionario de widgets basado en los campos del modelo
    widgets_dict = {}
    model_fields = model._meta.get_fields()
    
    for field in model_fields:
        # Solo procesar campos directos (no relaciones inversas)
        if hasattr(field, 'name'):
            field_name = field.name
            # Verificar si el campo debe incluirse
            if fields and field_name not in fields:
                continue
            if field_name in exclude:
                continue
            # Solo agregar si es un campo del modelo (no relaciones inversas)
            if hasattr(field, 'model') and field.model == model:
                widgets_dict[field_name] = get_widget_for_field(field)
    
    # Crear ModelForm con widgets
    FormClass = modelform_factory(
        model, 
        fields=fields, 
        exclude=exclude,
        widgets=widgets_dict if widgets_dict else None
    )
    
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
    
    # Solo admin y gerente pueden crear objetos desde admin
    # BODEGA (employee) y CONSULTA (viewer) NO pueden acceder
    if role not in ['admin', 'manager'] and not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para crear objetos. Solo administradores y gerentes pueden realizar esta acción.')
        return redirect('admin_panel' if role in ['admin', 'manager'] else 'dashboard')
    
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
    
    # Crear diccionario de widgets basado en los campos del modelo
    widgets_dict = {}
    model_fields = model._meta.get_fields()
    
    for field in model_fields:
        # Solo procesar campos directos (no relaciones inversas)
        if hasattr(field, 'name'):
            field_name = field.name
            # Verificar si el campo debe incluirse
            if fields and field_name not in fields:
                continue
            if field_name in exclude:
                continue
            # Solo agregar si es un campo del modelo (no relaciones inversas)
            if hasattr(field, 'model') and field.model == model:
                widgets_dict[field_name] = get_widget_for_field(field)
    
    # Crear ModelForm con widgets
    FormClass = modelform_factory(
        model, 
        fields=fields, 
        exclude=exclude,
        widgets=widgets_dict if widgets_dict else None
    )
    
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
    
    # Solo admin y gerente pueden crear objetos desde admin
    # BODEGA (employee) y CONSULTA (viewer) NO pueden acceder
    if role not in ['admin', 'manager'] and not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para crear objetos. Solo administradores y gerentes pueden realizar esta acción.')
        return redirect('admin_panel' if role in ['admin', 'manager'] else 'dashboard')
    
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


@login_required
@require_http_methods(["GET"])
def admin_model_export_excel(request, app_label, model_name):
    """Exportar objetos de un modelo a Excel"""
    from openpyxl import Workbook
    from django.http import HttpResponse
    from django.utils import timezone
    
    role = get_user_role(request)
    
    # Solo admin y gerente pueden acceder
    if not (request.user.is_staff or role in ['admin', 'manager']):
        messages.error(request, 'No tienes permiso para exportar datos.')
        return redirect('dashboard')
    
    model = get_model_from_string(app_label, model_name)
    if not model:
        messages.error(request, 'Modelo no encontrado.')
        return redirect('admin_panel')
    
    # Verificar permisos
    if not check_permission(request, app_label, model_name, 'view'):
        messages.error(request, 'No tienes permiso para exportar este modelo.')
        return redirect('admin_panel')
    
    model_admin = get_model_admin(app_label, model_name)
    
    # Obtener queryset (aplicar los mismos filtros que en la lista)
    queryset = model.objects.all()
    
    # Aplicar filtros del admin si existen
    if model_admin and hasattr(model_admin, 'get_queryset'):
        queryset = model_admin.get_queryset(request)
    
    # Aplicar búsqueda si existe
    search_query = request.GET.get('q', '')
    if search_query and model_admin and hasattr(model_admin, 'search_fields'):
        search_fields = model_admin.search_fields
        search_filter = Q()
        for field in search_fields:
            if '__' in field:
                search_filter |= Q(**{f'{field}__icontains': search_query})
            else:
                search_filter |= Q(**{f'{field}__icontains': search_query})
        queryset = queryset.filter(search_filter)
    
    # Ordenamiento
    if model_admin and hasattr(model_admin, 'ordering'):
        queryset = queryset.order_by(*model_admin.ordering)
    
    # Obtener campos para mostrar
    list_display = ['__str__']
    if model_admin and hasattr(model_admin, 'list_display'):
        list_display = model_admin.list_display
    
    # Crear workbook
    wb = Workbook()
    ws = wb.active
    ws.title = model._meta.verbose_name_plural[:31]  # Excel limita a 31 caracteres
    
    # Encabezados
    headers = []
    for field in list_display:
        if field == '__str__':
            headers.append('Nombre')
        else:
            # Intentar obtener el nombre legible del campo
            try:
                field_obj = model._meta.get_field(field)
                headers.append(field_obj.verbose_name.title())
            except:
                headers.append(field.replace('_', ' ').title())
    ws.append(headers)
    
    # Datos
    for obj in queryset:
        row = []
        for field in list_display:
            if field == '__str__':
                row.append(str(obj))
            else:
                try:
                    if '__' in field:
                        # Campo relacionado
                        parts = field.split('__')
                        value = obj
                        for part in parts:
                            value = getattr(value, part, None)
                            if value is None:
                                break
                        row.append(str(value) if value is not None else '')
                    else:
                        # Campo directo
                        value = getattr(obj, field, None)
                        if callable(value):
                            value = value()
                        row.append(str(value) if value is not None else '')
                except Exception:
                    row.append('')
        ws.append(row)
    
    # Respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    now = timezone.now()
    if timezone.is_naive(now):
        timestamp = now.strftime('%Y%m%d_%H%M%S')
    else:
        timestamp = timezone.localtime(now).strftime('%Y%m%d_%H%M%S')
    
    filename = f"{model._meta.verbose_name_plural.replace(' ', '_')}_{timestamp}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb.save(response)
    return response

