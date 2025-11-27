"""
Formularios para creación de usuarios desde el panel de administración
"""
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from organizations.models import Organization
from .models import Cliente, ProveedorUser, UserProfile, validate_rut_chileno
from .utils import generate_temporary_password, send_temporary_password_email


class AdminUserCreationForm(UserCreationForm):
    """Formulario base para creación de usuarios desde admin"""
    email = forms.EmailField(
        required=True,
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'maxlength': '254'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'maxlength': '150'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'maxlength': '150'
        })
    )
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all().order_by('name'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Organización',
        empty_label='Seleccione una organización'
    )
    role = forms.ChoiceField(
        choices=[
            ('admin', 'Administrador'),
            ('manager', 'Gerente'),
            ('employee', 'Empleado'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Rol'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '150'}),
        }
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar campos de contraseña
        if 'password1' in self.fields:
            del self.fields['password1']
        if 'password2' in self.fields:
            del self.fields['password2']
    
    def clean_role(self):
        """Validar que el rol sea obligatorio"""
        role = self.cleaned_data.get('role')
        if not role:
            raise forms.ValidationError('El rol es obligatorio.')
        return role
    
    def clean(self):
        """Validaciones adicionales"""
        cleaned_data = super().clean()
        
        # Validar que el estado sea 'ACTIVO' por defecto (ya está en el modelo)
        # No necesitamos validar estado aquí porque siempre será ACTIVO para nuevos usuarios
        
        return cleaned_data
    
    def save(self, commit=True, request=None):
        # Generar contraseña provisoria
        temporary_password = generate_temporary_password()
        
        # Crear usuario con contraseña provisoria
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=temporary_password,
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )
        
        if commit:
            # Crear perfil de usuario con must_change_password=True
            UserProfile.objects.create(
                user=user,
                organization=self.cleaned_data['organization'],
                role=self.cleaned_data['role'],
                state='ACTIVO',  # Estado obligatorio, siempre ACTIVO para nuevos
                mfa_enabled=False,
                must_change_password=True
            )
            
            # Guardar contraseña en la sesión para mostrarla al administrador
            if request:
                request.session[f'generated_password_{user.id}'] = temporary_password
            
            # Enviar correo con contraseña provisoria
            send_temporary_password_email(user, temporary_password, request)
        
        # Guardar la contraseña en el objeto user para poder accederla después
        user._temporary_password = temporary_password
        return user


class AdminClienteCreationForm(UserCreationForm):
    """Formulario para crear clientes desde admin"""
    email = forms.EmailField(
        required=True,
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'maxlength': '254'})
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '150'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '150'})
    )
    rut = forms.CharField(
        max_length=12,
        required=True,
        validators=[validate_rut_chileno],
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '12', 'placeholder': '12345678-9'})
    )
    phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '30'})
    )
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all().order_by('name'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Organización',
        empty_label='Seleccione una organización'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '150'}),
        }
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar campos de contraseña
        if 'password1' in self.fields:
            del self.fields['password1']
        if 'password2' in self.fields:
            del self.fields['password2']
    
    def clean(self):
        """Validaciones adicionales"""
        cleaned_data = super().clean()
        
        # Validar que el rol sea 'cliente' (implícito pero explícito)
        # El estado siempre será ACTIVO para nuevos usuarios
        
        return cleaned_data
    
    def save(self, commit=True, request=None):
        # Generar contraseña provisoria
        temporary_password = generate_temporary_password()
        
        # Crear usuario con contraseña provisoria
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=temporary_password,
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )
        
        if commit:
            # Crear cliente
            Cliente.objects.create(
                user=user,
                rut=self.cleaned_data['rut'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                phone=self.cleaned_data.get('phone', '')
            )
            # Crear perfil con must_change_password=True
            UserProfile.objects.create(
                user=user,
                organization=self.cleaned_data['organization'],
                role='cliente',  # Rol fijo para clientes
                phone=self.cleaned_data.get('phone', ''),
                state='ACTIVO',  # Estado obligatorio, siempre ACTIVO para nuevos
                mfa_enabled=False,
                must_change_password=True
            )
            
            # Guardar contraseña en la sesión para mostrarla al administrador
            if request:
                request.session[f'generated_password_{user.id}'] = temporary_password
            
            # Enviar correo con contraseña provisoria
            send_temporary_password_email(user, temporary_password, request)
        
        # Guardar la contraseña en el objeto user para poder accederla después
        user._temporary_password = temporary_password
        return user


class AdminProveedorCreationForm(UserCreationForm):
    """Formulario para crear proveedores desde admin"""
    email = forms.EmailField(
        required=True,
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'maxlength': '254'})
    )
    razon_social = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '200'})
    )
    nombre_fantasia = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '200'})
    )
    rut = forms.CharField(
        max_length=12,
        required=True,
        validators=[validate_rut_chileno],
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '12', 'placeholder': '12345678-9'})
    )
    phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '30'})
    )
    
    # Campos adicionales de datos de contacto
    direccion = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '200'})
    )
    ciudad = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'})
    )
    pais = forms.CharField(
        max_length=100,
        required=True,  # País es obligatorio
        initial='Chile',
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'})
    )
    sitio_web = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'maxlength': '200'})
    )
    
    # Campos de condiciones comerciales
    plazo_pago = forms.IntegerField(
        required=False,
        initial=30,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    )
    moneda = forms.ChoiceField(
        choices=[
            ('CLP', 'Peso Chileno (CLP)'),
            ('USD', 'Dólar (USD)'),
            ('EUR', 'Euro (EUR)'),
        ],
        required=False,
        initial='CLP',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    condiciones_pago = forms.CharField(
        max_length=255,
        required=False,
        initial='Contado',
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '255'})
    )
    descuento = forms.DecimalField(
        required=False,
        initial=0,
        max_digits=5,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
    )
    
    # Campos de contacto principal
    contacto_principal_nombre = forms.CharField(
        max_length=120,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '120'})
    )
    contacto_principal_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'maxlength': '254'})
    )
    contacto_principal_telefono = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '30'})
    )
    
    # Otros campos
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3'})
    )
    es_preferente = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all().order_by('name'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Organización',
        empty_label='Seleccione una organización'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '150'}),
        }
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar campos de contraseña
        if 'password1' in self.fields:
            del self.fields['password1']
        if 'password2' in self.fields:
            del self.fields['password2']
    
    def clean_razon_social(self):
        """Validar que la razón social sea obligatoria"""
        razon_social = self.cleaned_data.get('razon_social')
        if not razon_social or not razon_social.strip():
            raise forms.ValidationError('La razón social es obligatoria.')
        return razon_social
    
    def clean_pais(self):
        """Validar que el país sea obligatorio"""
        pais = self.cleaned_data.get('pais')
        if not pais or not pais.strip():
            raise forms.ValidationError('El país es obligatorio.')
        return pais
    
    def save(self, commit=True, request=None):
        # Importar aquí para evitar importaciones circulares
        from production.models import Proveedor
        from decimal import Decimal
        
        # Generar contraseña provisoria
        temporary_password = generate_temporary_password()
        
        # Crear usuario con contraseña provisoria
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=temporary_password,
            first_name=self.cleaned_data.get('razon_social', ''),
        )
        
        if commit:
            # Crear ProveedorUser
            ProveedorUser.objects.create(
                user=user,
                rut=self.cleaned_data['rut'],
                razon_social=self.cleaned_data['razon_social'],
                nombre_fantasia=self.cleaned_data.get('nombre_fantasia', ''),
                email=self.cleaned_data['email'],
                phone=self.cleaned_data.get('phone', '')
            )
            
            # Crear o actualizar el registro en el modelo Proveedor (production)
            Proveedor.objects.update_or_create(
                rut=self.cleaned_data['rut'],
                defaults={
                    'razon_social': self.cleaned_data['razon_social'],
                    'nombre_fantasia': self.cleaned_data.get('nombre_fantasia', ''),
                    'email': self.cleaned_data['email'],
                    'telefono': self.cleaned_data.get('phone', ''),
                    'sitio_web': self.cleaned_data.get('sitio_web', ''),
                    'direccion': self.cleaned_data.get('direccion', ''),
                    'ciudad': self.cleaned_data.get('ciudad', ''),
                    'pais': self.cleaned_data.get('pais', 'Chile'),
                    'plazo_pago': self.cleaned_data.get('plazo_pago', 30),
                    'moneda': self.cleaned_data.get('moneda', 'CLP'),
                    'condiciones_pago': self.cleaned_data.get('condiciones_pago', 'Contado'),
                    'descuento': self.cleaned_data.get('descuento', Decimal('0.00')),
                    'contacto_principal_nombre': self.cleaned_data.get('contacto_principal_nombre', ''),
                    'contacto_principal_email': self.cleaned_data.get('contacto_principal_email', ''),
                    'contacto_principal_telefono': self.cleaned_data.get('contacto_principal_telefono', ''),
                    'observaciones': self.cleaned_data.get('observaciones', ''),
                    'estado': 'ACTIVO',
                    'es_preferente': self.cleaned_data.get('es_preferente', False)
                }
            )
            
            # Crear perfil con must_change_password=True
            UserProfile.objects.create(
                user=user,
                organization=self.cleaned_data['organization'],
                role='proveedor',
                phone=self.cleaned_data.get('phone', ''),
                state='ACTIVO',
                mfa_enabled=False,
                must_change_password=True
            )
            
            # Guardar contraseña en la sesión para mostrarla al administrador
            if request:
                request.session[f'generated_password_{user.id}'] = temporary_password
            
            # Enviar correo con contraseña provisoria
            send_temporary_password_email(user, temporary_password, request)
        
        # Guardar la contraseña en el objeto user para poder accederla después
        user._temporary_password = temporary_password
        return user

