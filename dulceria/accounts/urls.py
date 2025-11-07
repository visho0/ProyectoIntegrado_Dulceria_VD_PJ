from django.urls import path
from . import views
from . import password_reset_views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),  # Usar vista personalizada
    path('register/', views.register_cliente, name='register_cliente'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('exportar-usuarios/', views.export_users_excel, name='export_users_excel'),
    
    # Recuperación de contraseña
    path('password-reset/', password_reset_views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', password_reset_views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', password_reset_views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', password_reset_views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]