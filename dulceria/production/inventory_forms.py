"""
Formularios para el módulo de inventario
"""
from django import forms
from django.core.validators import MinValueValidator
from .models import MovimientoInventario, Bodega, Product, Proveedor


class MovimientoInventarioForm(forms.ModelForm):
    """Formulario para registrar movimientos de inventario"""
    
    class Meta:
        model = MovimientoInventario
        fields = [
            'fecha', 'tipo', 'producto', 'proveedor', 'bodega', 'cantidad',
            'lote', 'serie', 'fecha_vencimiento',
            'doc_referencia', 'observaciones', 'motivo'
        ]
        widgets = {
            'fecha': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'bodega': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'lote': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '50',
                'placeholder': 'L-2025-001'
            }),
            'serie': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '50',
                'placeholder': 'SN123456789'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'doc_referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100',
                'placeholder': 'OC-123 / FAC-456 / GUIA-789'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas de operación, recibo, daño, etc.'
            }),
            'motivo': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '255',
                'placeholder': 'Diferencia inventario, devolución cliente, etc.'
            }),
        }
        labels = {
            'fecha': 'Fecha y Hora',
            'tipo': 'Tipo de Movimiento',
            'producto': 'Producto',
            'proveedor': 'Proveedor',
            'bodega': 'Bodega',
            'cantidad': 'Cantidad',
            'lote': 'Lote',
            'serie': 'Serie',
            'fecha_vencimiento': 'Fecha de Vencimiento',
            'doc_referencia': 'Documento de Referencia',
            'observaciones': 'Observaciones',
            'motivo': 'Motivo',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar productos activos y aprobados
        self.fields['producto'].queryset = Product.objects.filter(
            is_active=True,
            estado_aprobacion='APROBADO'
        ).order_by('name')
        
        # Filtrar proveedores activos
        self.fields['proveedor'].queryset = Proveedor.objects.filter(
            estado='ACTIVO'
        ).order_by('razon_social')
        
        # Filtrar bodegas activas
        self.fields['bodega'].queryset = Bodega.objects.filter(
            is_active=True
        ).order_by('codigo')
        
        # Hacer proveedor opcional
        self.fields['proveedor'].required = False
        
        # Si es edición, hacer algunos campos readonly
        if self.instance and self.instance.pk:
            self.fields['fecha'].widget.attrs['readonly'] = True
            self.fields['tipo'].widget.attrs['readonly'] = True
            self.fields['producto'].widget.attrs['readonly'] = True
    
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is not None and cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a 0.')
        return cantidad
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        proveedor = cleaned_data.get('proveedor')
        
        # Validar que ingresos tengan proveedor
        if tipo == 'ingreso' and not proveedor:
            raise forms.ValidationError({
                'proveedor': 'Los movimientos de ingreso deben tener un proveedor asociado.'
            })
        
        return cleaned_data

