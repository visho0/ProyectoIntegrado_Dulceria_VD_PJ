from django import forms
from django.core.validators import MinValueValidator
from .models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'ean_upc', 'description', 'category', 'marca', 'modelo',
            'imagen', 'imagen_url', 'ficha_tecnica_url',
            'uom_compra', 'uom_venta', 'factor_conversion',
            'costo_estandar', 'costo_promedio', 'price', 'iva',
            'stock', 'stock_minimo', 'stock_maximo', 'punto_reorden',
            'es_perecible', 'control_por_lote', 'control_por_serie',
            'fecha_vencimiento', 'mes_vencimiento',
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '200'}),
            'ean_upc': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '50'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': '150'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'imagen_url': forms.URLInput(attrs={'class': 'form-control'}),
            'ficha_tecnica_url': forms.URLInput(attrs={'class': 'form-control'}),
            'uom_compra': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10'}),
            'uom_venta': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10'}),
            'factor_conversion': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': '0.0001'}),
            'costo_estandar': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'costo_promedio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'iva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'stock_maximo': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'punto_reorden': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'es_perecible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'control_por_lote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'control_por_serie': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'mes_vencimiento': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Nombre del Producto',
            'ean_upc': 'EAN / UPC',
            'description': 'Descripción',
            'category': 'Categoría',
            'marca': 'Marca',
            'modelo': 'Modelo',
            'imagen': 'Imagen del Producto',
            'imagen_url': 'Imagen (URL)',
            'ficha_tecnica_url': 'Ficha técnica (URL)',
            'uom_compra': 'Unidad de compra',
            'uom_venta': 'Unidad de venta',
            'factor_conversion': 'Factor de conversión',
            'costo_estandar': 'Costo Estándar',
            'costo_promedio': 'Costo Promedio',
            'price': 'Precio de Venta',
            'iva': 'IVA (%)',
            'stock': 'Stock Actual',
            'stock_minimo': 'Stock Mínimo',
            'stock_maximo': 'Stock Máximo',
            'punto_reorden': 'Punto de Reorden',
            'es_perecible': 'Producto Perecible',
            'control_por_lote': 'Control por lote',
            'control_por_serie': 'Control por serie',
            'fecha_vencimiento': 'Fecha de Vencimiento',
            'mes_vencimiento': 'Mes de Vencimiento',
            'is_active': 'Activo',
        }
    
    def __init__(self, *args, **kwargs):
        user_role = kwargs.pop('user_role', None)
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        # Campo SKU solo informativo
        self.fields['sku'] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            label='SKU'
        )
        self.fields['sku'].disabled = True
        if instance and instance.sku:
            self.fields['sku'].initial = instance.sku
        else:
            self.fields['sku'].initial = 'Se generará automáticamente'
        
        # Configurar mes_vencimiento con nombres de meses
        self.fields['mes_vencimiento'].widget = forms.Select(attrs={'class': 'form-control'})
        self.fields['mes_vencimiento'].choices = [
            ('', 'Seleccione un mes'),
            (1, 'Enero'),
            (2, 'Febrero'),
            (3, 'Marzo'),
            (4, 'Abril'),
            (5, 'Mayo'),
            (6, 'Junio'),
            (7, 'Julio'),
            (8, 'Agosto'),
            (9, 'Septiembre'),
            (10, 'Octubre'),
            (11, 'Noviembre'),
            (12, 'Diciembre'),
        ]
        
        # Si es proveedor, ocultar campos que no puede editar
        if user_role == 'proveedor':
            # Ocultar campos que solo el gerente puede modificar
            if 'is_active' in self.fields:
                del self.fields['is_active']
            if 'estado_aprobacion' in self.fields:
                del self.fields['estado_aprobacion']
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description) > 150:
            raise forms.ValidationError('La descripción no puede exceder 150 caracteres.')
        return description
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validar que los valores no sean negativos
        campos_numericos = ['costo_estandar', 'costo_promedio', 'price', 'iva',
                          'stock', 'stock_minimo', 'stock_maximo', 'punto_reorden']
        
        for campo in campos_numericos:
            valor = cleaned_data.get(campo)
            if valor is not None and valor < 0:
                raise forms.ValidationError({campo: f'El valor de {self.fields[campo].label} no puede ser negativo.'})
        
        # Validar mes de vencimiento
        mes_vencimiento = cleaned_data.get('mes_vencimiento')
        if mes_vencimiento is not None and (mes_vencimiento < 1 or mes_vencimiento > 12):
            raise forms.ValidationError({'mes_vencimiento': 'El mes de vencimiento debe estar entre 1 y 12.'})
        
        # Validar IVA
        iva = cleaned_data.get('iva')
        if iva is not None and (iva < 0 or iva > 100):
            raise forms.ValidationError({'iva': 'El IVA debe estar entre 0 y 100%.'})
        
        factor = cleaned_data.get('factor_conversion')
        if factor is not None and factor < 0.0001:
            raise forms.ValidationError({'factor_conversion': 'El factor de conversión debe ser mayor a 0.'})
        
        stock_minimo = cleaned_data.get('stock_minimo') or 0
        stock_maximo = cleaned_data.get('stock_maximo')
        if stock_maximo is not None and stock_maximo < stock_minimo:
            raise forms.ValidationError({'stock_maximo': 'El stock máximo no puede ser menor al stock mínimo.'})
        
        return cleaned_data

