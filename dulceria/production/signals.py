from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product, Category


@receiver(post_delete, sender=Product)
def actualizar_sku_despues_eliminar(sender, instance, **kwargs):
    """Actualizar los SKU de los productos restantes después de eliminar uno"""
    # Obtener todos los productos ordenados por ID
    productos = Product.objects.all().order_by('id')
    
    # Renumerar los SKU
    for index, producto in enumerate(productos, start=1):
        nuevo_sku = f"SKU-{str(index).zfill(3)}"
        if producto.sku != nuevo_sku:
            producto.sku = nuevo_sku
            # Usar update para evitar recursión
            Product.objects.filter(pk=producto.pk).update(sku=nuevo_sku)
    
    # Invalidar caché de dashboard después de eliminar producto
    cache.delete('dashboard_total_products')


@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def invalidar_cache_productos(sender, instance, **kwargs):
    """Invalidar caché relacionado con productos"""
    # Invalidar caché de conteos
    cache.delete('dashboard_total_products')
    # Invalidar caché de listas (si existe)
    try:
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern('products_list_*')
    except Exception:
        pass


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def invalidar_cache_categorias(sender, instance, **kwargs):
    """Invalidar caché relacionado con categorías"""
    cache.delete('dashboard_total_categories')
    cache.delete('categorias_list')
    try:
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern('categories_overview_*')
    except Exception:
        pass

