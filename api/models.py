from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.db.models import F, Sum


class UsuarioCustom(AbstractUser):
    telefono = models.CharField(max_length=20, blank=True, null=True)


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'

    def __str__(self):
        return self.nombre


class Editorial(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'editoriales'

    def __str__(self):
        return self.nombre


class Autor(models.Model):
    nombre = models.CharField(max_length=150)
    biografia = models.TextField(blank=True)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'autores'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    titulo = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    editorial = models.ForeignKey(Editorial, on_delete=models.PROTECT, related_name='productos')
    autores = models.ManyToManyField(Autor, related_name='obras')

    class Meta:
        ordering = ['titulo']

    def __str__(self):
        return self.titulo


class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE)
    cantidad_disponible = models.PositiveIntegerField(default=0)
    pasillo = models.CharField(max_length=10)

    class Meta:
        ordering = ['producto__titulo']
        verbose_name_plural = 'inventarios'

    def __str__(self):
        return f'{self.producto} - {self.cantidad_disponible} u. (pasillo {self.pasillo})'


class Cliente(models.Model):
    usuario = models.OneToOneField(UsuarioCustom, on_delete=models.CASCADE)
    direccion_envio = models.TextField()
    ciudad = models.CharField(max_length=100)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.usuario.get_username()} ({self.ciudad})'


class Pedido(models.Model):
    ESTADOS = (
        ('P', 'Pendiente'),
        ('E', 'Enviado'),
        ('C', 'Cancelado'),
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=1, choices=ESTADOS, default='P')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'Pedido #{self.pk} - {self.cliente} ({self.get_estado_display()})'

    def recalcular_total(self):
        total = self.detalles.aggregate(
            total=Sum(
                F('cantidad') * F('precio_unitario'),
                output_field=models.DecimalField(max_digits=12, decimal_places=2),
            )
        )['total'] or Decimal('0.00')
        self.total = total
        self.save(update_fields=['total'])
        return total

    @transaction.atomic
    def cancelar(self):
        for detalle in self.detalles.all():
            detalle.devolver_stock()
        self.estado = 'C'
        self.save(update_fields=['estado'])


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['id']
        verbose_name = 'detalle de pedido'
        verbose_name_plural = 'detalles de pedido'

    def __str__(self):
        return f'{self.cantidad} x {self.producto} (pedido #{self.pedido_id})'

    def devolver_stock(self):
        Inventario.objects.filter(producto=self.producto).update(
            cantidad_disponible=F('cantidad_disponible') + self.cantidad
        )


class Resena(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='resenas')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    puntaje = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comentario = models.TextField()

    class Meta:
        ordering = ['-id']
        verbose_name = 'reseña'
        verbose_name_plural = 'reseñas'
        constraints = [
            models.UniqueConstraint(fields=['producto', 'cliente'], name='resena_unica_por_cliente_producto'),
        ]

    def __str__(self):
        return f'{self.producto} - {self.puntaje}/5 por {self.cliente}'
