from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.products_list, name="products_list"),
    path("products/create/", views.product_create, name="product_create"),
    path("products/edit/<int:pk>/", views.product_edit, name="product_edit"),
]
