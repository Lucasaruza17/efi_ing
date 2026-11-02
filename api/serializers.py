from rest_framework import serializers
from .models import Categoria, Editorial, Autor, Producto, Cliente, Pedido, DetallePedido, Resena

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

# --- SERIALIZADORES DE PRODUCTO ---
class ProductoSerializer(serializers.ModelSerializer):
    # Serializador plano para POST/PUT/PATCH/GET(id)
    class Meta:
        model = Producto
        fields = '__all__'

class ProductoListSerializer(serializers.ModelSerializer):
    # Serializador anidado exclusivo para GET ALL (List)
    categoria = CategoriaSerializer(read_only=True)
    editorial = EditorialSerializer(read_only=True)
    autores = AutorSerializer(many=True, read_only=True)

    class Meta:
        model = Producto
        fields = '__all__'

# --- SERIALIZADORES DE PEDIDO ---
class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class DetallePedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedido
        fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
    # Serializador plano
    class Meta:
        model = Pedido
        fields = '__all__'

class PedidoListSerializer(serializers.ModelSerializer):
    # Serializador anidado exclusivo para GET ALL (List)
    cliente = ClienteSerializer(read_only=True)
    detalles = DetallePedidoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = '__all__'

class ResenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resena
        fields = '__all__'