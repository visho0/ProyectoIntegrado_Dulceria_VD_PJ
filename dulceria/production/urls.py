from django.urls import path
from . import views
from . import admin_views
from . import inventory_views

urlpatterns = [
    # CRUD de productos
    path("products/", views.products_list, name="products_list"),
    path("products/create/", views.product_create, name="product_create"),
    path("products/edit/<int:pk>/", views.product_edit, name="product_edit"),
    path("products/delete/<int:pk>/", views.product_delete_ajax, name="product_delete_ajax"),
    path("categories/", views.categories_overview, name="categories_overview"),
    
    # Tienda online (clientes)
    path("tienda/", views.tienda_online, name="tienda_online"),
    path("tienda/add_to_cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("carrito/", views.view_cart, name="view_cart"),
    path("carrito/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("carrito/update/<int:product_id>/", views.update_cart_quantity, name="update_cart_quantity"),
    
    # Administración integrada
    path("admin-panel/", views.admin_panel, name="admin_panel"),
    
    # Vistas genéricas del admin
    path("admin-panel/<str:app_label>/<str:model_name>/", admin_views.admin_model_list, name="admin_model_list"),
    path("admin-panel/<str:app_label>/<str:model_name>/add/", admin_views.admin_model_create, name="admin_model_create"),
    path("admin-panel/<str:app_label>/<str:model_name>/<int:pk>/edit/", admin_views.admin_model_edit, name="admin_model_edit"),
    path("admin-panel/<str:app_label>/<str:model_name>/<int:pk>/delete/", admin_views.admin_model_delete, name="admin_model_delete"),
    
    # Vista de proveedor
    path("proveedor/", views.proveedor_dashboard, name="proveedor_dashboard"),
    
    # Aprobación de productos
    path("aprobar-productos/", views.aprobar_productos, name="aprobar_productos"),
    
    # Módulo de inventario
    path("inventario/", inventory_views.inventory_dashboard, name="inventory_dashboard"),
    path("inventario/movimientos/", inventory_views.movimientos_list, name="movimientos_list"),
    path("inventario/movimientos/crear/", inventory_views.movimiento_create, name="movimiento_create"),
    path("inventario/movimientos/<int:pk>/editar/", inventory_views.movimiento_edit, name="movimiento_edit"),
    path("inventario/movimientos/<int:pk>/eliminar/", inventory_views.movimiento_delete, name="movimiento_delete"),
    path("inventario/exportar-excel/", inventory_views.export_inventory_excel, name="export_inventory_excel"),
]
