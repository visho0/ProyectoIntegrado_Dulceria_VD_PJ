"""
Comando para generar datos de prueba para pruebas de stress/rendimiento
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import random
from datetime import datetime, timedelta

from production.models import Product, Category, Proveedor, MovimientoInventario, Bodega, ProductoProveedor
from accounts.models import ProveedorUser, UserProfile
from organizations.models import Organization


class Command(BaseCommand):
    help = 'Genera datos de prueba para pruebas de stress/rendimiento (proveedores, productos, movimientos)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--proveedores',
            type=int,
            default=100,
            help='Número de proveedores a crear (default: 100)'
        )
        parser.add_argument(
            '--productos',
            type=int,
            default=1000,
            help='Número de productos a crear (default: 1000)'
        )
        parser.add_argument(
            '--movimientos',
            type=int,
            default=1000,
            help='Número de movimientos a crear (default: 1000)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular sin crear datos reales'
        )

    def handle(self, *args, **options):
        num_proveedores = options['proveedores']
        num_productos = options['productos']
        num_movimientos = options['movimientos']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: No se crearán datos reales'))

        # Obtener o crear organización
        org = Organization.objects.filter(name__iexact='Red de Proveedores').first()
        if not org:
            org = Organization.objects.filter(name__iexact='Dulcería Central').first()
        if not org:
            org = Organization.objects.create(name='Red de Proveedores')

        # Obtener categorías
        categorias = list(Category.objects.all())
        if not categorias:
            self.stdout.write(self.style.ERROR('No hay categorías. Ejecuta primero: python manage.py create_categorias_dulces'))
            return

        # Obtener bodegas
        bodegas = list(Bodega.objects.filter(is_active=True))
        if not bodegas:
            self.stdout.write(self.style.ERROR('No hay bodegas. Ejecuta primero: python manage.py create_bodegas'))
            return

        # Obtener usuario admin para crear movimientos
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('No hay usuario admin. Crea uno primero.'))
            return

        # Nombres y datos ficticios
        nombres_empresas = [
            'Dulces', 'Confites', 'Golosinas', 'Chocolates', 'Caramelos',
            'Snacks', 'Importadora', 'Distribuidora', 'Comercial', 'Industria'
        ]
        apellidos_empresas = [
            'Del Sur', 'Del Norte', 'Andina', 'Pacífico', 'Cordillera',
            'Valparaíso', 'Santiago', 'Concepción', 'Chile', 'Latina'
        ]
        ciudades = ['Santiago', 'Valparaíso', 'Concepción', 'Viña del Mar', 'La Serena', 'Antofagasta']
        nombres_dulces = [
            'Chocolate', 'Caramelo', 'Gomita', 'Galleta', 'Alfajor',
            'Turrón', 'Chicle', 'Paleta', 'Regaliz', 'Bombón',
            'Truffle', 'Barra', 'Tableta', 'Mini', 'Mix'
        ]
        sabores = [
            'Fresa', 'Vainilla', 'Chocolate', 'Menta', 'Naranja',
            'Limón', 'Manzana', 'Plátano', 'Uva', 'Cereza'
        ]

        # Generar proveedores
        self.stdout.write(f'Generando {num_proveedores} proveedores...')
        proveedores_creados = []
        
        with transaction.atomic():
            for i in range(1, num_proveedores + 1):
                nombre_empresa = f"{random.choice(nombres_empresas)} {random.choice(apellidos_empresas)} {i}"
                rut_numero = 10000000 + i
                rut_dv = self.calcular_dv(rut_numero)
                rut = f"{rut_numero}-{rut_dv}"
                
                if not dry_run:
                    try:
                        # Crear usuario
                        username = f"proveedor_{i:04d}"
                        email = f"proveedor{i}@test.com"
                        
                        if User.objects.filter(username=username).exists():
                            continue
                        
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            password='test123456',
                            first_name=nombre_empresa
                        )
                        
                        # Crear ProveedorUser
                        proveedor_user = ProveedorUser.objects.create(
                            user=user,
                            rut=rut,
                            razon_social=nombre_empresa,
                            nombre_fantasia=f"{nombre_empresa} S.A.",
                            email=email,
                            phone=f"+569{random.randint(10000000, 99999999)}"
                        )
                        
                        # Crear UserProfile
                        UserProfile.objects.create(
                            user=user,
                            organization=org,
                            role='proveedor',
                            phone=proveedor_user.phone,
                            state='ACTIVO'
                        )
                        
                        # Crear Proveedor (modelo comercial)
                        proveedor = Proveedor.objects.create(
                            rut=rut,
                            razon_social=nombre_empresa,
                            nombre_fantasia=f"{nombre_empresa} S.A.",
                            email=email,
                            telefono=proveedor_user.phone,
                            ciudad=random.choice(ciudades),
                            pais='Chile',
                            estado='ACTIVO',
                            plazo_pago=random.choice([15, 30, 45, 60]),
                            moneda='CLP',
                            condiciones_pago='30 días',
                            descuento=Decimal(random.uniform(0, 10))
                        )
                        
                        proveedores_creados.append(proveedor)
                        
                        if i % 50 == 0:
                            self.stdout.write(f'  Creados {i} proveedores...')
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error al crear proveedor {i}: {str(e)}'))
                        continue
                else:
                    proveedores_creados.append(None)

        self.stdout.write(self.style.SUCCESS(f'✅ {len(proveedores_creados)} proveedores procesados'))

        # Generar productos
        self.stdout.write(f'Generando {num_productos} productos...')
        productos_creados = []
        
        with transaction.atomic():
            for i in range(1, num_productos + 1):
                nombre = f"{random.choice(nombres_dulces)} {random.choice(sabores)} {i}"
                categoria = random.choice(categorias)
                
                if not dry_run:
                    try:
                        producto = Product.objects.create(
                            name=nombre,
                            category=categoria,
                            description=f"Descripción del producto {nombre}",
                            price=Decimal(random.uniform(100, 5000)),
                            costo_estandar=Decimal(random.uniform(50, 2500)),
                            stock=random.randint(0, 1000),
                            stock_minimo=random.randint(10, 100),
                            is_active=True,
                            estado_aprobacion='APROBADO',
                            uom_compra='UN',
                            uom_venta='UN'
                        )
                        
                        productos_creados.append(producto)
                        
                        if i % 100 == 0:
                            self.stdout.write(f'  Creados {i} productos...')
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error al crear producto {i}: {str(e)}'))
                        continue
                else:
                    productos_creados.append(None)

        self.stdout.write(self.style.SUCCESS(f'✅ {len(productos_creados)} productos procesados'))

        # Asignar productos a proveedores (ProductoProveedor)
        if proveedores_creados and productos_creados and not dry_run:
            self.stdout.write('Asignando productos a proveedores...')
            for producto in productos_creados[:500]:  # Limitar para no sobrecargar
                proveedor = random.choice(proveedores_creados)
                ProductoProveedor.objects.get_or_create(
                    product=producto,
                    proveedor=proveedor,
                    defaults={
                        'costo': producto.costo_estandar or Decimal('100'),
                        'lead_time': random.randint(3, 15),
                        'min_lote': Decimal('10.000000'),
                        'descuento_pct': Decimal(random.uniform(0, 5))
                    }
                )

        # Generar movimientos
        if productos_creados and not dry_run:
            self.stdout.write(f'Generando {num_movimientos} movimientos...')
            tipos = ['ingreso', 'salida', 'ajuste', 'devolucion']
            
            # Crear movimientos en lotes para mejor rendimiento
            batch_size = 100
            movimientos_batch = []
            
            with transaction.atomic():
                for i in range(num_movimientos):
                    producto = random.choice(productos_creados)
                    proveedor = random.choice(proveedores_creados) if proveedores_creados else None
                    bodega = random.choice(bodegas)
                    tipo = random.choice(tipos)
                    
                    # Fechas aleatorias en los últimos 6 meses
                    fecha = timezone.now() - timedelta(days=random.randint(0, 180))
                    
                    try:
                        movimiento = MovimientoInventario(
                            fecha=fecha,
                            tipo=tipo,
                            producto=producto,
                            proveedor=proveedor if tipo == 'ingreso' else None,
                            bodega=bodega,
                            cantidad=Decimal(random.uniform(1, 100)),
                            creado_por=admin_user,
                            doc_referencia=f"DOC-{random.randint(1000, 9999)}"
                        )
                        movimientos_batch.append(movimiento)
                        
                        # Crear en lotes para mejor rendimiento
                        if len(movimientos_batch) >= batch_size:
                            MovimientoInventario.objects.bulk_create(movimientos_batch, ignore_conflicts=True)
                            movimientos_batch = []
                            
                            if (i + 1) % 500 == 0:
                                self.stdout.write(f'  Creados {i + 1} movimientos...')
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error al preparar movimiento {i}: {str(e)}'))
                        continue
                
                # Crear los últimos movimientos restantes
                if movimientos_batch:
                    MovimientoInventario.objects.bulk_create(movimientos_batch, ignore_conflicts=True)

            # Actualizar stock de productos después de crear todos los movimientos
            self.stdout.write('Actualizando stock de productos...')
            from django.db.models import Sum, Case, When, F
            from django.db.models.functions import Coalesce
            
            # Calcular stock total por producto basado en movimientos
            for producto in productos_creados[:100]:  # Limitar para no sobrecargar
                try:
                    movimientos_producto = MovimientoInventario.objects.filter(producto=producto)
                    stock_ingreso = movimientos_producto.filter(tipo__in=['ingreso', 'devolucion']).aggregate(
                        total=Sum('cantidad')
                    )['total'] or 0
                    stock_salida = movimientos_producto.filter(tipo='salida').aggregate(
                        total=Sum('cantidad')
                    )['total'] or 0
                    stock_ajuste = movimientos_producto.filter(tipo='ajuste').aggregate(
                        total=Sum('cantidad')
                    )['total'] or 0
                    
                    stock_total = int(float(stock_ingreso) - float(stock_salida) + float(stock_ajuste))
                    producto.stock = max(0, stock_total)
                    producto.save(update_fields=['stock'])
                except Exception as e:
                    continue

            self.stdout.write(self.style.SUCCESS(f'✅ {num_movimientos} movimientos creados'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Proceso completado! Datos generados exitosamente.'
            )
        )

    def calcular_dv(self, rut_numero):
        """Calcular dígito verificador de RUT chileno"""
        rut_str = str(rut_numero)
        suma = 0
        multiplo = 2
        
        for r in reversed(rut_str):
            suma += int(r) * multiplo
            multiplo += 1
            if multiplo > 7:
                multiplo = 2
        
        resto = suma % 11
        dv = 11 - resto if resto != 0 else 0
        
        if dv == 10:
            return 'K'
        elif dv == 11:
            return '0'
        return str(dv)
