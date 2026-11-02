from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CategoriaViewSet, EditorialViewSet, AutorViewSet, 
                    ProductoViewSet, ClienteViewSet, PedidoViewSet, 
                    DetallePedidoViewSet, ResenaViewSet)

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'editoriales', EditorialViewSet)
router.register(r'autores', AutorViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'pedidos', PedidoViewSet)
router.register(r'detalles', DetallePedidoViewSet)
router.register(r'resenas', ResenaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]