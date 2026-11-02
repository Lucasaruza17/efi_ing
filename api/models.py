from django.db import models
from django.contrib.auth.models import AbstractUser

class UsuarioCustom(AbstractUser):
    telefono = models.CharField(max_length=20, blank=True, null=True)

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Editorial(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nombre

class Autor(models.Model):
    nombre = models.CharField(max_length=150)
    biografia = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    titulo = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    editorial = models.ForeignKey(Editorial, on_delete=models.CASCADE, related_name='productos')
    autores = models.ManyToManyField(Autor, related_name='obras')

    def __str__(self):
        return self.titulo

class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE)
    cantidad_disponible = models.PositiveIntegerField(default=0)
    pasillo = models.CharField(max_length=10)

class Cliente(models.Model):
    usuario = models.OneToOneField(UsuarioCustom, on_delete=models.CASCADE)
    direccion_envio = models.TextField()
    ciudad = models.CharField(max_length=100)

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

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

class Resena(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='resenas')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    puntaje = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comentario = models.TextField()
# Create your models here.
