from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (AutorViewSet, CategoriaViewSet, ClienteViewSet, DetallePedidoViewSet,
                    EditorialViewSet, InventarioViewSet, LoginView, LogoutView, MeView, PedidoViewSet,
                    ProductoViewSet, RegistroView, ResenaViewSet)

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'editoriales', EditorialViewSet)
router.register(r'autores', AutorViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'inventario', InventarioViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'pedidos', PedidoViewSet)
router.register(r'detalles', DetallePedidoViewSet)
router.register(r'resenas', ResenaViewSet)

urlpatterns = [
    # Autenticación por token
    path('auth/registro/', RegistroView.as_view(), name='registro'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('', include(router.urls)),
]
