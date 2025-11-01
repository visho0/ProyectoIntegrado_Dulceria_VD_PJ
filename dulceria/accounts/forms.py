from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import Cliente


class LoginForm(AuthenticationForm):
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


class ClienteRegistrationForm(UserCreationForm):
    """Formulario de registro para clientes"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@correo.com'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu apellido'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56912345678'
        })
    )
    rut = forms.CharField(
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345678-9'
        }),
        help_text='Formato: 12345678-9'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña'
        })

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
        return user
