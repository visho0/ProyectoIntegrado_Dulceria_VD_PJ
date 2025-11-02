from django.urls import path
from . import views

urlpatterns = [
    # CRUD de productos
    path("products/", views.products_list, name="products_list"),
    path("products/create/", views.product_create, name="product_create"),
    path("products/edit/<int:pk>/", views.product_edit, name="product_edit"),
    path("products/delete/<int:pk>/", views.product_delete_ajax, name="product_delete_ajax"),
    
    # Tienda online (clientes)
    path("tienda/", views.tienda_online, name="tienda_online"),
    path("tienda/add_to_cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("carrito/", views.view_cart, name="view_cart"),
    path("carrito/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("carrito/update/<int:product_id>/", views.update_cart_quantity, name="update_cart_quantity"),
]
