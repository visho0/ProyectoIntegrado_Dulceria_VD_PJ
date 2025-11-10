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
        rut = self.cleaned_data.get('rut')
        # Validar que solo contenga números, guión y K
        rut_limpio = rut.replace('.', '').replace('-', '')
        if not rut_limpio[:-1].isdigit():
            raise forms.ValidationError('El RUT solo debe contener números (excepto el dígito verificador)')
        return rut

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('razon_social', '')
        if commit:
            user.save()
            # Crear el perfil de proveedor
            ProveedorUser.objects.create(
                user=user,
                rut=self.cleaned_data['rut'],
                razon_social=self.cleaned_data['razon_social'],
                nombre_fantasia=self.cleaned_data.get('nombre_fantasia', ''),
                email=self.cleaned_data['email'],
                phone=self.cleaned_data['phone']
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

