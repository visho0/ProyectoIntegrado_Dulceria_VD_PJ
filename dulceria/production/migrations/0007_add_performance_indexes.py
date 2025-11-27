# Generated manually for MySQL compatibility with prefix indexes
from django.db import migrations


def create_indexes(apps, schema_editor):
    """Crear índices con prefijos para MySQL"""
    db_alias = schema_editor.connection.alias
    
    with schema_editor.connection.cursor() as cursor:
        # Índices para Product - usando prefijos para campos largos (compatible con MySQL)
        # Índice en name con prefijo (primeros 100 caracteres = 400 bytes máximo)
        try:
            cursor.execute("CREATE INDEX prod_name_idx ON production_product (name(100));")
        except Exception:
            pass  # Índice ya existe
        
        # Índices compuestos solo con campos pequeños
        try:
            cursor.execute("CREATE INDEX prod_active_aprob_idx ON production_product (is_active, estado_aprobacion);")
        except Exception:
            pass
        
        try:
            cursor.execute("CREATE INDEX prod_cat_active_idx ON production_product (category_id, is_active);")
        except Exception:
            pass
        
        # Índices para Proveedor - usando prefijos para campos largos
        try:
            cursor.execute("CREATE INDEX prov_razon_social_idx ON production_proveedor (razon_social(100));")
        except Exception:
            pass
        
        try:
            cursor.execute("CREATE INDEX prov_email_idx ON production_proveedor (email(100));")
        except Exception:
            pass
        
        try:
            cursor.execute("CREATE INDEX prov_estado_idx ON production_proveedor (estado);")
        except Exception:
            pass
        
        # Índices adicionales para MovimientoInventario
        try:
            cursor.execute("CREATE INDEX mov_tipo_fecha_idx ON production_movimientoinventario (tipo, fecha DESC);")
        except Exception:
            pass


def drop_indexes(apps, schema_editor):
    """Eliminar índices"""
    db_alias = schema_editor.connection.alias
    
    with schema_editor.connection.cursor() as cursor:
        indexes_to_drop = [
            'prod_name_idx',
            'prod_active_aprob_idx',
            'prod_cat_active_idx',
            'prov_razon_social_idx',
            'prov_email_idx',
            'prov_estado_idx',
            'mov_tipo_fecha_idx',
        ]
        
        for index_name in indexes_to_drop:
            try:
                if 'prod_' in index_name:
                    cursor.execute(f"DROP INDEX {index_name} ON production_product;")
                elif 'prov_' in index_name:
                    cursor.execute(f"DROP INDEX {index_name} ON production_proveedor;")
                elif 'mov_' in index_name:
                    cursor.execute(f"DROP INDEX {index_name} ON production_movimientoinventario;")
            except Exception:
                pass  # Índice no existe


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0006_alter_productoproveedor_lead_time'),
    ]

    operations = [
        migrations.RunPython(create_indexes, reverse_code=drop_indexes),
    ]
