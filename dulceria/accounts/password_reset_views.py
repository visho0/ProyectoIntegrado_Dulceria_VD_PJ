"""
Vistas personalizadas para recuperación de contraseña
"""
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CustomPasswordResetForm


class CustomPasswordResetView(PasswordResetView):
    """Vista para solicitar recuperación de contraseña"""
    template_name = 'accounts/password_reset.html'
    form_class = CustomPasswordResetForm
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        """
        Siempre mostrar mensaje de éxito, incluso si el email no existe.
        Esto previene revelar información sobre qué emails están registrados.
        """
        # Intentar enviar el email (solo se envía si el email existe)
        form.save(request=self.request)
        # Siempre redirigir a la página de éxito
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Mostrar mensajes de error apropiados"""
        messages.error(
            self.request,
            'Por favor, corrige los errores en el formulario.'
        )
        return super().form_invalid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Vista que confirma que se envió el email"""
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Vista para establecer nueva contraseña con validación mejorada de tokens"""
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    
    def dispatch(self, *args, **kwargs):
        """Verificar si el token es válido antes de mostrar el formulario"""
        try:
            response = super().dispatch(*args, **kwargs)
            # Si el token es inválido, el método padre redirige automáticamente
            return response
        except Exception as e:
            # Si hay un error con el token (expirado o inválido)
            messages.error(
                self.request,
                'El enlace de recuperación de contraseña es inválido o ha expirado. '
                'Por favor, solicita un nuevo enlace.'
            )
            return redirect('password_reset')
    
    def form_invalid(self, form):
        """Manejar errores de validación del formulario"""
        messages.error(
            self.request,
            'Por favor, corrige los errores en el formulario y asegúrate de que '
            'la nueva contraseña cumpla con los requisitos de seguridad.'
        )
        return super().form_invalid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Vista que confirma que la contraseña fue cambiada"""
    template_name = 'accounts/password_reset_complete.html'

