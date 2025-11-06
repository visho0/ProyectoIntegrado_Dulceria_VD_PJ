from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_userprofile_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='area',
            field=models.CharField(blank=True, max_length=120, verbose_name='Área/Unidad'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='mfa_enabled',
            field=models.BooleanField(default=False, verbose_name='MFA habilitado'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='observaciones',
            field=models.TextField(blank=True, verbose_name='Observaciones'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='sesiones_activas',
            field=models.PositiveIntegerField(default=0, verbose_name='Sesiones activas'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='state',
            field=models.CharField(choices=[('ACTIVO', 'Activo'), ('BLOQUEADO', 'Bloqueado')], default='ACTIVO', max_length=20, verbose_name='Estado'),
        ),
    ]

