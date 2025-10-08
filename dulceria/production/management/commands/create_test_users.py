from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from organizations.models import Organization
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Crea usuarios de prueba con diferentes roles'

    def handle(self, *args, **options):
        # Obtener o crear organizaciones
        org_fabrica, created = Organization.objects.get_or_create(
            name="Fábrica",
            defaults={'name': 'Fábrica'}
        )
        
        org_sucursal, created = Organization.objects.get_or_create(
            name="Sucursal 1 Mall Plaza",
            defaults={'name': 'Sucursal 1 Mall Plaza'}
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Organización "{org_fabrica.name}" creada')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Organización "{org_sucursal.name}" creada')
            )

        # Crear grupos de roles
        admin_group, created = Group.objects.get_or_create(name='admin')
        manager_group, created = Group.objects.get_or_create(name='manager')
        employee_group, created = Group.objects.get_or_create(name='employee')

        # Crear usuario admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@dulceria.com',
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Usuario admin creado')
            )

        # Crear perfil para admin
        admin_profile, created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'organization': org_fabrica,
                'role': 'admin'
            }
        )
        admin_user.groups.add(admin_group)

        # Crear usuario gerente
        manager_user, created = User.objects.get_or_create(
            username='gerente',
            defaults={
                'email': 'gerente@dulceria.com',
                'first_name': 'Gerente',
                'last_name': 'Ventas',
                'is_staff': True  # Necesita staff para acceder al admin
            }
        )
        manager_user.set_password('gerente123')
        manager_user.is_staff = True  # Asegurar que tenga acceso al admin
        manager_user.save()
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Usuario gerente creado')
            )

        # Crear perfil para gerente
        manager_profile, created = UserProfile.objects.get_or_create(
            user=manager_user,
            defaults={
                'organization': org_sucursal,
                'role': 'manager'
            }
        )
        manager_user.groups.add(manager_group)

        # Crear usuario empleado
        employee_user, created = User.objects.get_or_create(
            username='empleado',
            defaults={
                'email': 'empleado@dulceria.com',
                'first_name': 'Empleado',
                'last_name': 'Ventas',
                'is_staff': False
            }
        )
        employee_user.set_password('empleado123')
        employee_user.save()
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Usuario empleado creado')
            )

        # Crear perfil para empleado
        employee_profile, created = UserProfile.objects.get_or_create(
            user=employee_user,
            defaults={
                'organization': org_sucursal,
                'role': 'employee'
            }
        )
        employee_user.groups.add(employee_group)

        self.stdout.write(
            self.style.SUCCESS('\nUsuarios de prueba creados:')
        )
        self.stdout.write(
            self.style.WARNING('Admin: admin / admin123 (Fábrica)')
        )
        self.stdout.write(
            self.style.WARNING('Gerente: gerente / gerente123 (Sucursal 1 Mall Plaza)')
        )
        self.stdout.write(
            self.style.WARNING('Empleado: empleado / empleado123 (Sucursal 1 Mall Plaza)')
        )

