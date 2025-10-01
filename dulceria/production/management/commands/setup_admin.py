from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from organizations.models import Organization
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Configura el usuario administrador y su perfil'

    def handle(self, *args, **options):
        # Obtener o crear la organización
        org, created = Organization.objects.get_or_create(
            name="Dulcería Central",
            defaults={'name': 'Dulcería Central'}
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Organización "{org.name}" creada')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Organización "{org.name}" ya existe')
            )

        # Obtener el usuario admin
        try:
            admin_user = User.objects.get(username='admin')
            
            # Establecer contraseña
            admin_user.set_password('admin123')
            admin_user.save()
            
            # Crear o actualizar perfil
            profile, created = UserProfile.objects.get_or_create(
                user=admin_user,
                defaults={
                    'organization': org,
                    'role': 'admin'
                }
            )
            
            if not created:
                profile.organization = org
                profile.role = 'admin'
                profile.save()
            
            self.stdout.write(
                self.style.SUCCESS('Usuario admin configurado correctamente')
            )
            self.stdout.write(
                self.style.WARNING('Usuario: admin')
            )
            self.stdout.write(
                self.style.WARNING('Contraseña: admin123')
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Usuario admin no encontrado. Ejecuta: python manage.py createsuperuser')
            )
