from django.urls import path
from . import views
from . import password_reset_views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),  # Usar vista personalizada
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('exportar-usuarios/', views.export_users_excel, name='export_users_excel'),
    path('accounts/admin/crear-usuario/', views.create_user_admin, name='create_user_admin'),
    
    # Recuperación de contraseña
    path('password-reset/', password_reset_views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', password_reset_views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', password_reset_views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', password_reset_views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Cambio de contraseña obligatorio
    path('change-password-required/', views.change_password_required, name='change_password_required'),
    
    # Reset de contraseña por administrador
    path('accounts/admin/reset-password/<int:user_id>/', views.reset_user_password, name='reset_user_password'),
    
    # Página de éxito después de crear usuario
    path('accounts/admin/user-created-success/', views.user_created_success, name='user_created_success'),
]