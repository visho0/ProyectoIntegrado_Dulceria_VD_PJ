from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.contrib.auth.models import User
from organizations.models import Organization
from .models import Cliente, ProveedorUser, UserProfile


class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(
        required=False,
        label="Recordarme",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "form-control", 
            "placeholder": "Usuario o email"
        })
        self.fields["password"].widget.attrs.update({
            "class": "form-control", 
            "placeholder": "Contraseña"
        })
        self.fields["remember_me"].widget.attrs.update({
            "class": "form-check-input"
        })


class ClienteRegistrationForm(UserCreationForm):
    """Formulario de registro para clientes"""
    email = forms.EmailField(
        required=True,
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@correo.com',
            'maxlength': '254'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre',
            'maxlength': '150'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu apellido',
            'maxlength': '150'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56912345678',
            'maxlength': '20'
        })
    )
    rut = forms.CharField(
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345678-9',
            'maxlength': '12',
            'pattern': '[0-9]{7,8}-[0-9Kk]',
            'oninput': 'this.value = this.value.replace(/[^0-9Kk-]/g, "")'
        }),
        help_text='Formato: 12345678-9 (solo números y guión)'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'maxlength': '150'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña'
        })

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        # Validar que solo contenga números, guión y K
        rut_limpio = rut.replace('.', '').replace('-', '')
        if not rut_limpio[:-1].isdigit():
            raise forms.ValidationError('El RUT solo debe contener números (excepto el dígito verificador)')
        return rut

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Crear el perfil de cliente
            Cliente.objects.create(
                user=user,
                rut=self.cleaned_data['rut'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                phone=self.cleaned_data['phone']
            )
            organization = self._get_default_organization()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'organization': organization,
                    'role': 'cliente',
                    'phone': self.cleaned_data['phone'],
                    'state': 'ACTIVO',
                    'mfa_enabled': False
                }
            )
        return user

    @staticmethod
    def _get_default_organization():
        organization = Organization.objects.filter(name__iexact='Dulcería Central').first()
        if not organization:
            organization = Organization.objects.first()
        if not organization:
            organization = Organization.objects.create(name='Dulcería Central')
        return organization

class ProveedorRegistrationForm(UserCreationForm):
    """Formulario de registro para proveedores"""
    email = forms.EmailField(
        required=True,
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'contacto@empresa.com',
            'maxlength': '254'
        })
    )
    razon_social = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Razón Social',
            'maxlength': '200'
        })
    )
    nombre_fantasia = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de Fantasía (opcional)',
            'maxlength': '200'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56912345678',
            'maxlength': '20'
        })
    )
    rut = forms.CharField(
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345678-9',
            'maxlength': '12',
            'pattern': '[0-9]{7,8}-[0-9Kk]',
            'oninput': 'this.value = this.value.replace(/[^0-9Kk-]/g, "")'
        }),
        help_text='Formato: 12345678-9 (solo números y guión)'
    )
    
    # Campos adicionales del modelo Proveedor (production)
    sitio_web = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://www.ejemplo.com',
            'maxlength': '200'
        }),
        help_text='Sitio web de la empresa (opcional)'
    )
    direccion = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dirección completa',
            'maxlength': '200'
        })
    )
    ciudad = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ciudad',
            'maxlength': '100'
        })
    )
    pais = forms.CharField(
        max_length=100,
        required=True,  # País es obligatorio
        initial='Chile',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'País',
            'maxlength': '100'
        })
    )
    plazo_pago = forms.IntegerField(
        required=False,
        initial=30,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1'
        }),
        help_text='Plazo de pago en días (por defecto 30)'
    )
    moneda = forms.ChoiceField(
        choices=[
            ('CLP', 'Peso Chileno (CLP)'),
            ('USD', 'Dólar (USD)'),
            ('EUR', 'Euro (EUR)'),
        ],
        required=False,
        initial='CLP',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    condiciones_pago = forms.CharField(
        max_length=255,
        required=False,
        initial='Contado',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contado, 30 días, etc.',
            'maxlength': '255'
        })
    )
    descuento = forms.DecimalField(
        required=False,
        initial=0,
        max_digits=5,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        }),
        help_text='Descuento porcentual (0-100)'
    )
    contacto_principal_nombre = forms.CharField(
        max_length=120,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del contacto principal',
            'maxlength': '120'
        })
    )
    contacto_principal_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@contacto.com',
            'maxlength': '254'
        })
    )
    contacto_principal_telefono = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56912345678',
            'maxlength': '30'
        })
    )
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '3',
            'placeholder': 'Observaciones adicionales (opcional)'
        })
    )
    es_preferente = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Marcar si desea ser considerado proveedor preferente'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'maxlength': '150'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña'
        })

    def clean_rut(self):
        """Validar que el RUT sea obligatorio y tenga formato correcto"""
        rut = self.cleaned_data.get('rut')
        if not rut or not rut.strip():
            raise forms.ValidationError('El RUT es obligatorio.')
        # Validar que solo contenga números, guión y K
        rut_limpio = rut.replace('.', '').replace('-', '')
        if not rut_limpio[:-1].isdigit():
            raise forms.ValidationError('El RUT solo debe contener números (excepto el dígito verificador)')
        return rut
    
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

    def save(self, commit=True):
        # Importar aquí para evitar importaciones circulares
        from production.models import Proveedor
        
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('razon_social', '')
        if commit:
            user.save()
            
            # Crear el perfil de proveedor (ProveedorUser)
            proveedor_user = ProveedorUser.objects.create(
                user=user,
                rut=self.cleaned_data['rut'],
                razon_social=self.cleaned_data['razon_social'],
                nombre_fantasia=self.cleaned_data.get('nombre_fantasia', ''),
                email=self.cleaned_data['email'],
                phone=self.cleaned_data['phone']
            )
            
            # Crear también el registro en el modelo Proveedor (production)
            Proveedor.objects.update_or_create(
                rut=self.cleaned_data['rut'],
                defaults={
                    'razon_social': self.cleaned_data['razon_social'],
                    'nombre_fantasia': self.cleaned_data.get('nombre_fantasia', ''),
                    'sitio_web': self.cleaned_data.get('sitio_web', ''),
                    'email': self.cleaned_data['email'],
                    'telefono': self.cleaned_data.get('phone', ''),
                    'direccion': self.cleaned_data.get('direccion', ''),
                    'ciudad': self.cleaned_data.get('ciudad', ''),
                    'pais': self.cleaned_data.get('pais', 'Chile'),
                    'plazo_pago': self.cleaned_data.get('plazo_pago', 30),
                    'moneda': self.cleaned_data.get('moneda', 'CLP'),
                    'condiciones_pago': self.cleaned_data.get('condiciones_pago', 'Contado'),
                    'descuento': self.cleaned_data.get('descuento', 0),
                    'contacto_principal_nombre': self.cleaned_data.get('contacto_principal_nombre', ''),
                    'contacto_principal_email': self.cleaned_data.get('contacto_principal_email', ''),
                    'contacto_principal_telefono': self.cleaned_data.get('contacto_principal_telefono', ''),
                    'observaciones': self.cleaned_data.get('observaciones', ''),
                    'estado': 'ACTIVO',
                    'es_preferente': self.cleaned_data.get('es_preferente', False)
                }
            )
            
            organization = self._get_default_organization()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'organization': organization,
                    'role': 'proveedor',
                    'phone': self.cleaned_data['phone'],
                    'state': 'ACTIVO',
                    'mfa_enabled': False
                }
            )
        return user

    @staticmethod
    def _get_default_organization():
        organization = Organization.objects.filter(name__iexact='Red de Proveedores').first()
        if not organization:
            organization = Organization.objects.filter(name__iexact='Dulcería Central').first()
        if not organization:
            organization = Organization.objects.first()
        if not organization:
            organization = Organization.objects.create(name='Red de Proveedores')
        return organization


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '150'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '150'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'maxlength': '254'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone', 'area', 'observaciones', 'mfa_enabled', 'avatar')
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '20'}),
            'area': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '120'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'mfa_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and avatar.size > 3 * 1024 * 1024:
            raise forms.ValidationError('La imagen no debe superar los 3 MB.')
        return avatar


class ProveedorUserForm(forms.ModelForm):
    """Formulario para editar datos del proveedor"""
    class Meta:
        model = ProveedorUser
        fields = ('rut', 'razon_social', 'nombre_fantasia', 'email', 'phone')
        widgets = {
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '12',
                'pattern': '[0-9]{7,8}-[0-9Kk]',
                'oninput': 'this.value = this.value.replace(/[^0-9Kk-]/g, "")'
            }),
            'razon_social': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '200'}),
            'nombre_fantasia': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '200'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'maxlength': '254'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '20'}),
        }
        labels = {
            'rut': 'RUT',
            'razon_social': 'Razón Social',
            'nombre_fantasia': 'Nombre de Fantasía',
            'email': 'Correo Electrónico',
            'phone': 'Teléfono',
        }


from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm


class CustomPasswordResetForm(DjangoPasswordResetForm):
    """Formulario personalizado para recuperación de contraseña"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ingresa tu correo electrónico',
            'autocomplete': 'email',
            'maxlength': '254'
        })
        self.fields['email'].label = 'Correo Electrónico'
        self.fields['email'].help_text = 'Ingresa el correo electrónico asociado a tu cuenta.'
        self.fields['email'].required = True
    
    def clean_email(self):
        """Validar formato de email (no revelar si existe o no por seguridad)"""
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('El correo electrónico es obligatorio.')
        
        # Validar formato básico
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError as DjangoValidationError
        try:
            validate_email(email)
        except DjangoValidationError:
            raise forms.ValidationError('Por favor, ingresa un correo electrónico válido.')
        
        return email
    
    def save(self, domain_override=None,
             subject_template_name='accounts/password_reset_subject.txt',
             email_template_name='accounts/password_reset_email.html',
             use_https=False, token_generator=None,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Sobrescribir save para no revelar si el email existe o no.
        Django por defecto solo envía email si existe, pero queremos mostrar siempre el mismo mensaje.
        """
        # Llamar al método padre para enviar el email si existe
        email = self.cleaned_data.get("email")
        if not email:
            return True
        
        # Llamar al método padre - esto enviará el correo si el email existe
        # El método padre retorna el número de correos enviados (0 si no existe el email)
        # No capturamos excepciones aquí para que el backend de consola funcione correctamente
        result = super().save(
            domain_override=domain_override,
            subject_template_name=subject_template_name,
            email_template_name=email_template_name,
            use_https=use_https,
            token_generator=token_generator,
            from_email=from_email,
            request=request,
            html_email_template_name=html_email_template_name,
            extra_email_context=extra_email_context
        )
        
        # Siempre retornar True para no revelar si el email existe
        # (incluso si result es 0 porque el email no existe)
        return True


from django.contrib.auth.forms import SetPasswordForm


class RequiredPasswordChangeForm(SetPasswordForm):
    """Formulario para cambio de contraseña obligatorio"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nueva contraseña',
            'autocomplete': 'new-password',
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña',
            'autocomplete': 'new-password',
        })
        self.fields['new_password1'].label = 'Nueva Contraseña'
        self.fields['new_password2'].label = 'Confirmar Nueva Contraseña'
        self.fields['new_password1'].help_text = 'Tu contraseña debe contener al menos 8 caracteres, incluyendo mayúsculas, minúsculas, números y caracteres especiales.'
