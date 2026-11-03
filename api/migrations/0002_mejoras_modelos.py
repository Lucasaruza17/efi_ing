import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        # Orden por defecto y nombres legibles
        migrations.AlterModelOptions(
            name='categoria',
            options={'ordering': ['nombre'], 'verbose_name': 'categoría', 'verbose_name_plural': 'categorías'},
        ),
        migrations.AlterModelOptions(
            name='editorial',
            options={'ordering': ['nombre'], 'verbose_name_plural': 'editoriales'},
        ),
        migrations.AlterModelOptions(
            name='autor',
            options={'ordering': ['nombre'], 'verbose_name_plural': 'autores'},
        ),
        migrations.AlterModelOptions(
            name='producto',
            options={'ordering': ['titulo']},
        ),
        migrations.AlterModelOptions(
            name='inventario',
            options={'ordering': ['producto__titulo'], 'verbose_name_plural': 'inventarios'},
        ),
        migrations.AlterModelOptions(
            name='cliente',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='pedido',
            options={'ordering': ['-fecha_creacion']},
        ),
        migrations.AlterModelOptions(
            name='detallepedido',
            options={'ordering': ['id'], 'verbose_name': 'detalle de pedido', 'verbose_name_plural': 'detalles de pedido'},
        ),
        migrations.AlterModelOptions(
            name='resena',
            options={'ordering': ['-id'], 'verbose_name': 'reseña', 'verbose_name_plural': 'reseñas'},
        ),
        # CASCADE -> PROTECT
        migrations.AlterField(
            model_name='producto',
            name='categoria',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='productos', to='api.categoria'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='editorial',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='productos', to='api.editorial'),
        ),
        migrations.AlterField(
            model_name='detallepedido',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.producto'),
        ),
        # Un cliente solo puede reseñar una vez cada producto
        migrations.AddConstraint(
            model_name='resena',
            constraint=models.UniqueConstraint(fields=('producto', 'cliente'), name='resena_unica_por_cliente_producto'),
        ),
    ]
