from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Categoria, Editorial, Autor, Producto, Cliente, Pedido, DetallePedido, Resena
from .serializers import (CategoriaSerializer, EditorialSerializer, AutorSerializer, 
                          ProductoSerializer, ProductoListSerializer, ClienteSerializer, 
                          PedidoSerializer, PedidoListSerializer, DetallePedidoSerializer, ResenaSerializer)

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class EditorialViewSet(viewsets.ModelViewSet):
    queryset = Editorial.objects.all()
    serializer_class = EditorialSerializer

class AutorViewSet(viewsets.ModelViewSet):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'editorial']
    search_fields = ['titulo', 'isbn']
    ordering_fields = ['precio', 'titulo']

    def get_serializer_class(self):
        # Lógica para mostrar datos anidados SOLO si es listado general (get all)
        if self.action == 'list':
            return ProductoListSerializer
        return ProductoSerializer

    # Función personalizada 1
    @action(detail=False, methods=['get'])
    def economicos(self, request):
        """Retorna productos menores a 10.000"""
        productos = self.get_queryset().filter(precio__lt=10000)
        page = self.paginate_queryset(productos)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()

    def get_serializer_class(self):
        # Lógica para mostrar datos anidados SOLO si es listado general (get all)
        if self.action == 'list':
            return PedidoListSerializer
        return PedidoSerializer

    # Función personalizada 2
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancela un pedido específico"""
        pedido = self.get_object()
        if pedido.estado == 'C':
            return Response({'detail': 'El pedido ya está cancelado'}, status=status.HTTP_400_BAD_REQUEST)
        pedido.estado = 'C'
        pedido.save()
        return Response({'detail': 'Pedido cancelado con éxito'})

class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer

class ResenaViewSet(viewsets.ModelViewSet):
    queryset = Resena.objects.all()
    serializer_class = ResenaSerializer

# Create your views here.
