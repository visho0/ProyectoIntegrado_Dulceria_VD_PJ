"""
Comando para crear categorías de dulces para la dulcería
"""
from django.core.management.base import BaseCommand
from production.models import Category


class Command(BaseCommand):
    help = 'Crea las categorías de dulces para la dulcería'

    def handle(self, *args, **options):
        categorias = [
            {
                'name': 'Chocolates',
                'description': 'Chocolates de diversas marcas y tipos: negro, con leche, blanco, rellenos, etc.'
            },
            {
                'name': 'Caramelos',
                'description': 'Caramelos duros, blandos, de fruta, ácidos, y de diversos sabores'
            },
            {
                'name': 'Gomitas',
                'description': 'Gomitas, jellies, ositos, gusanos y otras formas de gomitas'
            },
            {
                'name': 'Galletas',
                'description': 'Galletas dulces, de chocolate, cremas, wafers, y todo tipo de galletas'
            },
            {
                'name': 'Alfajores',
                'description': 'Alfajores de diversos tipos y rellenos'
            },
            {
                'name': 'Turrones',
                'description': 'Turrones duros, blandos, de diferentes sabores'
            },
            {
                'name': 'Chicles',
                'description': 'Chicles y gomas de mascar de todos los sabores'
            },
            {
                'name': 'Paletas',
                'description': 'Paletas de caramelo, heladas, y de diversos sabores'
            },
            {
                'name': 'Snacks Dulces',
                'description': 'Snacks dulces como barras de cereal, mix de frutos secos dulces, etc.'
            },
            {
                'name': 'Dulces Tradicionales',
                'description': 'Dulces tradicionales chilenos y latinoamericanos'
            },
            {
                'name': 'Regalices',
                'description': 'Regalices, regaliz y productos similares'
            },
            {
                'name': 'Bombones',
                'description': 'Bombones finos, trufas y chocolates de alta calidad'
            },
            {
                'name': 'Dulces Sin Azúcar',
                'description': 'Dulces y chocolates sin azúcar para personas diabéticas o dietas especiales'
            },
            {
                'name': 'Dulces Orgánicos',
                'description': 'Dulces y chocolates orgánicos y naturales'
            },
            {
                'name': 'Importados',
                'description': 'Dulces y chocolates importados de diversas partes del mundo'
            },
        ]
        
        created_count = 0
        skipped_count = 0
        
        for cat_data in categorias:
            categoria, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Categoría "{categoria.name}" creada exitosamente')
                )
            else:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Categoría "{categoria.name}" ya existe')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Proceso completado: {created_count} categorías creadas, {skipped_count} ya existían'
            )
        )
