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
from .forms import CustomPasswordResetForm


class CustomPasswordResetView(PasswordResetView):
    """Vista para solicitar recuperación de contraseña"""
    template_name = 'accounts/password_reset.html'
    form_class = CustomPasswordResetForm
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Vista que confirma que se envió el email"""
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Vista para establecer nueva contraseña"""
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Vista que confirma que la contraseña fue cambiada"""
    template_name = 'accounts/password_reset_complete.html'

