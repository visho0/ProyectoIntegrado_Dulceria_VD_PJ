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
                role='cliente',
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
    
    def save(self, commit=True, request=None):
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
            # Crear proveedor
            ProveedorUser.objects.create(
                user=user,
                rut=self.cleaned_data['rut'],
                razon_social=self.cleaned_data['razon_social'],
                nombre_fantasia=self.cleaned_data.get('nombre_fantasia', ''),
                email=self.cleaned_data['email'],
                phone=self.cleaned_data.get('phone', '')
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

