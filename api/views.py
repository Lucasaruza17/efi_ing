from django.db.models import ProtectedError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import ProductoFilter
from .models import Autor, Categoria, Cliente, DetallePedido, Editorial, Inventario, Pedido, Producto, Resena
from .permissions import EsDuenoOStaff, EsStaffOSoloLectura
from .serializers import (AutorSerializer, CategoriaSerializer, ClienteSerializer,
                          DetallePedidoSerializer, EditorialSerializer, InventarioSerializer,
                          PedidoListSerializer, PedidoSerializer, ProductoListSerializer,
                          ProductoSerializer, RegistroSerializer, ResenaSerializer)


class SoloLoPropioMixin:
    """El staff ve todo; el resto de los usuarios solo ve los registros que le pertenecen."""
    campo_dueno = 'usuario'

    def get_queryset(self):
        queryset = super().get_queryset()
        if getattr(self, 'swagger_fake_view', False):
            return queryset.none()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(**{self.campo_dueno: self.request.user})


class BorradoProtegidoMixin:
    """Si el registro tiene datos asociados (on_delete=PROTECT) responde 409 en lugar de romper con un 500."""

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {'detail': 'No se puede eliminar: hay registros que dependen de este elemento.'},
                status=status.HTTP_409_CONFLICT,
            )


def _cliente_de(user):
    cliente = Cliente.objects.filter(usuario=user).first()
    if cliente is None:
        raise ValidationError('Primero completá tu perfil de cliente en /api/clientes/.')
    return cliente


# ---------------------------------------------------------------- Catálogo (lectura pública, escritura staff)
class CategoriaViewSet(BorradoProtegidoMixin, viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [EsStaffOSoloLectura]
    search_fields = ['nombre']


class EditorialViewSet(BorradoProtegidoMixin, viewsets.ModelViewSet):
    queryset = Editorial.objects.all()
    serializer_class = EditorialSerializer
    permission_classes = [EsStaffOSoloLectura]
    search_fields = ['nombre', 'pais']


class AutorViewSet(viewsets.ModelViewSet):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer
    permission_classes = [EsStaffOSoloLectura]
    search_fields = ['nombre']


class ProductoViewSet(BorradoProtegidoMixin, viewsets.ModelViewSet):
    queryset = (Producto.objects
                .select_related('categoria', 'editorial', 'inventario')
                .prefetch_related('autores'))
    permission_classes = [EsStaffOSoloLectura]
    filterset_class = ProductoFilter
    search_fields = ['titulo', 'isbn']
    ordering_fields = ['precio', 'titulo']

    def get_serializer_class(self):
        # Datos anidados SOLO en el listado general (get all)
        if self.action == 'list':
            return ProductoListSerializer
        return ProductoSerializer

    # Función personalizada 1
    @extend_schema(responses=ProductoSerializer(many=True))
    @action(detail=False, methods=['get'])
    def economicos(self, request):
        """Retorna los productos con precio menor a $10.000."""
        productos = self.filter_queryset(self.get_queryset()).filter(precio__lt=10000)
        page = self.paginate_queryset(productos)
        serializer = ProductoSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    # Función personalizada 2
    @extend_schema(responses=ResenaSerializer(many=True))
    @action(detail=True, methods=['get'])
    def resenas(self, request, pk=None):
        """Retorna las reseñas de un producto (paginadas)."""
        producto = self.get_object()
        page = self.paginate_queryset(producto.resenas.all())
        serializer = ResenaSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.select_related('producto')
    serializer_class = InventarioSerializer
    permission_classes = [EsStaffOSoloLectura]
    filterset_fields = ['pasillo']
    search_fields = ['producto__titulo', 'pasillo']
    ordering_fields = ['cantidad_disponible']

    # Función personalizada 3
    @extend_schema(
        parameters=[OpenApiParameter('limite', int, description='Stock máximo a considerar (por defecto 5)')],
        responses=InventarioSerializer(many=True),
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def bajo_stock(self, request):
        """(Solo staff) Productos con poco stock para reponer."""
        try:
            limite = int(request.query_params.get('limite', 5))
        except ValueError:
            raise ValidationError({'limite': 'Debe ser un número entero.'})
        queryset = self.get_queryset().filter(cantidad_disponible__lte=limite).order_by('cantidad_disponible')
        page = self.paginate_queryset(queryset)
        return self.get_paginated_response(InventarioSerializer(page, many=True).data)


# ---------------------------------------------------------------- Clientes y pedidos (cada uno ve lo suyo)
class ClienteViewSet(SoloLoPropioMixin, viewsets.ModelViewSet):
    queryset = Cliente.objects.select_related('usuario')
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    campo_dueno = 'usuario'
    search_fields = ['usuario__username', 'ciudad']

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff and serializer.validated_data.get('usuario'):
            serializer.save()
            return
        if Cliente.objects.filter(usuario=user).exists():
            raise ValidationError('Ya tenés un perfil de cliente.')
        serializer.save(usuario=user)

    def perform_update(self, serializer):
        if self.request.user.is_staff:
            serializer.save()
        else:
            serializer.save(usuario=serializer.instance.usuario)

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied('Solo el staff puede eliminar clientes.')
        instance.delete()


class PedidoViewSet(SoloLoPropioMixin, viewsets.ModelViewSet):
    queryset = Pedido.objects.select_related('cliente__usuario').prefetch_related('detalles')
    permission_classes = [permissions.IsAuthenticated]
    campo_dueno = 'cliente__usuario'
    filterset_fields = ['estado']
    ordering_fields = ['fecha_creacion', 'total']

    def get_serializer_class(self):
        # Datos anidados SOLO en el listado general (get all)
        if self.action == 'list':
            return PedidoListSerializer
        return PedidoSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff and serializer.validated_data.get('cliente'):
            serializer.save()
        else:
            serializer.save(cliente=_cliente_de(user))

    def perform_update(self, serializer):
        if self.request.user.is_staff:
            serializer.save()
        else:
            serializer.save(cliente=serializer.instance.cliente)

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied('Para anular un pedido usá la acción "cancelar".')
        instance.delete()

    # Función personalizada 4
    @extend_schema(request=None, responses={200: OpenApiTypes.OBJECT})
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancela un pedido pendiente y devuelve el stock al inventario."""
        pedido = self.get_object()
        if pedido.estado == 'C':
            return Response({'detail': 'El pedido ya está cancelado'}, status=status.HTTP_400_BAD_REQUEST)
        if pedido.estado == 'E':
            return Response({'detail': 'No se puede cancelar un pedido que ya fue enviado'},
                            status=status.HTTP_400_BAD_REQUEST)
        pedido.cancelar()
        return Response({'detail': 'Pedido cancelado con éxito', 'estado': pedido.estado})

    # Función personalizada 5
    @extend_schema(request=None, responses={200: OpenApiTypes.OBJECT})
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def enviar(self, request, pk=None):
        """(Solo staff) Marca un pedido pendiente como enviado."""
        pedido = self.get_object()
        if pedido.estado != 'P':
            return Response({'detail': 'Solo se pueden enviar pedidos pendientes'},
                            status=status.HTTP_400_BAD_REQUEST)
        pedido.estado = 'E'
        pedido.save(update_fields=['estado'])
        return Response({'detail': 'Pedido marcado como enviado', 'estado': pedido.estado})


class DetallePedidoViewSet(SoloLoPropioMixin,
                           mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """Líneas de un pedido. Para cambiar una cantidad se elimina el detalle y se vuelve a crear."""
    queryset = DetallePedido.objects.select_related('pedido__cliente', 'producto')
    serializer_class = DetallePedidoSerializer
    permission_classes = [permissions.IsAuthenticated]
    campo_dueno = 'pedido__cliente__usuario'
    filterset_fields = ['pedido']

    def perform_destroy(self, instance):
        pedido = instance.pedido
        if pedido.estado != 'P':
            raise ValidationError('Solo se pueden quitar productos de pedidos pendientes.')
        instance.devolver_stock()
        instance.delete()
        pedido.recalcular_total()


class ResenaViewSet(viewsets.ModelViewSet):
    queryset = Resena.objects.select_related('producto', 'cliente__usuario')
    serializer_class = ResenaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, EsDuenoOStaff]
    filterset_fields = ['producto', 'puntaje']
    ordering_fields = ['puntaje']

    def perform_create(self, serializer):
        cliente = _cliente_de(self.request.user)
        if Resena.objects.filter(producto=serializer.validated_data['producto'], cliente=cliente).exists():
            raise ValidationError('Ya reseñaste este producto.')
        serializer.save(cliente=cliente)

    def perform_update(self, serializer):
        # No se puede mover una reseña a otro producto
        serializer.save(producto=serializer.instance.producto)


# ---------------------------------------------------------------- Autenticación por token
class RegistroView(generics.CreateAPIView):
    """Crea un usuario nuevo y devuelve su token."""
    serializer_class = RegistroSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'usuario': serializer.data}, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """Invalida el token del usuario autenticado."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
