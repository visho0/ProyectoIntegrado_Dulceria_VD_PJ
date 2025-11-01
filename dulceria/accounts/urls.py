from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register_cliente, name='register_cliente'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
]