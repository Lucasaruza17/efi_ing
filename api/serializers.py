from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.db.models import F
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from .models import (Autor, Categoria, Cliente, DetallePedido, Editorial, Inventario,
                     Pedido, Producto, Resena, UsuarioCustom)


# --- CATÁLOGO ---
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


class EditorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Editorial
        fields = '__all__'


class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = '__all__'


class InventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventario
        fields = '__all__'


# --- PRODUCTO ---
class ProductoSerializer(serializers.ModelSerializer):
    # Serializador plano para POST/PUT/PATCH/GET(id)
    class Meta:
        model = Producto
        fields = '__all__'

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError('El precio debe ser mayor a 0.')
        return value


class ProductoListSerializer(serializers.ModelSerializer):
    # Serializador anidado exclusivo para GET ALL (list)
    categoria = CategoriaSerializer(read_only=True)
    editorial = EditorialSerializer(read_only=True)
    autores = AutorSerializer(many=True, read_only=True)
    stock = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = '__all__'

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_stock(self, obj):
        inventario = getattr(obj, 'inventario', None)
        return inventario.cantidad_disponible if inventario else None


# --- CLIENTE ---
class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
        # Si no se envía, se toma el usuario autenticado
        extra_kwargs = {'usuario': {'required': False}}


# --- PEDIDO ---
class DetallePedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedido
        fields = '__all__'
        read_only_fields = ('precio_unitario',)

    def validate(self, attrs):
        pedido = attrs['pedido']
        producto = attrs['producto']
        cantidad = attrs['cantidad']
        request = self.context.get('request')

        if request and not request.user.is_staff and pedido.cliente.usuario_id != request.user.id:
            raise PermissionDenied('No podés agregar productos a un pedido que no es tuyo.')
        if pedido.estado != 'P':
            raise serializers.ValidationError('Solo se pueden agregar productos a pedidos pendientes.')
        if cantidad < 1:
            raise serializers.ValidationError({'cantidad': 'La cantidad debe ser al menos 1.'})

        inventario = Inventario.objects.filter(producto=producto).first()
        if inventario is None or inventario.cantidad_disponible < cantidad:
            disponible = inventario.cantidad_disponible if inventario else 0
            raise serializers.ValidationError(
                {'cantidad': f'Stock insuficiente. Disponible: {disponible}.'}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        producto = validated_data['producto']
        # El precio lo define el sistema (no el cliente) y queda "congelado" en el detalle
        validated_data['precio_unitario'] = producto.precio
        detalle = super().create(validated_data)
        Inventario.objects.filter(producto=producto).update(
            cantidad_disponible=F('cantidad_disponible') - detalle.cantidad
        )
        detalle.pedido.recalcular_total()
        return detalle


class PedidoSerializer(serializers.ModelSerializer):
    # Serializador plano
    class Meta:
        model = Pedido
        fields = '__all__'
        # El estado y el total los maneja el sistema (acciones y detalles), no el cliente
        read_only_fields = ('estado', 'total', 'fecha_creacion')
        extra_kwargs = {'cliente': {'required': False}}


class PedidoListSerializer(serializers.ModelSerializer):
    # Serializador anidado exclusivo para GET ALL (list)
    cliente = ClienteSerializer(read_only=True)
    detalles = DetallePedidoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = '__all__'


# --- RESEÑA ---
class ResenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resena
        fields = '__all__'
        read_only_fields = ('cliente',)


# --- AUTENTICACIÓN ---
class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = UsuarioCustom
        fields = ('id', 'username', 'email', 'password', 'telefono')

    def validate(self, attrs):
        validate_password(attrs['password'], user=UsuarioCustom(username=attrs['username'], email=attrs.get('email', '')))
        return attrs

    def create(self, validated_data):
        return UsuarioCustom.objects.create_user(**validated_data)


class UsuarioSerializer(serializers.ModelSerializer):
    """Datos básicos del usuario autenticado (el front usa is_staff para mostrar el panel de administración)."""
    class Meta:
        model = UsuarioCustom
        fields = ('id', 'username', 'email', 'telefono', 'is_staff')
        read_only_fields = fields
