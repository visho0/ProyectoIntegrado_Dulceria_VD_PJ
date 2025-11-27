from django.core.management.base import BaseCommand
from production.models import Bodega

class Command(BaseCommand):
    help = 'Crea las bodegas iniciales: Bodega Central y Sucursal 1'

    def handle(self, *args, **options):
        # Crear Bodega Central
        bodega_central, created = Bodega.objects.get_or_create(
            codigo='BOD-CENTRAL',
            defaults={
                'nombre': 'Bodega Central',
                'descripcion': 'Bodega principal de la empresa',
                'direccion': '',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Bodega "{bodega_central.nombre}" creada exitosamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Bodega "{bodega_central.nombre}" ya existe')
            )
        
        # Crear Sucursal 1
        sucursal_1, created = Bodega.objects.get_or_create(
            codigo='SUC-001',
            defaults={
                'nombre': 'Sucursal 1',
                'descripcion': 'Primera sucursal de la empresa',
                'direccion': '',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Bodega "{sucursal_1.nombre}" creada exitosamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Bodega "{sucursal_1.nombre}" ya existe')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Proceso completado')
        )

