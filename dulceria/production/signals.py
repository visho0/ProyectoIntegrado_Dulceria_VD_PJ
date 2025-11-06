from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Product


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

