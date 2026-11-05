from decimal import Decimal

from rest_framework.test import APITestCase

from .models import (Autor, Categoria, Cliente, Editorial, Inventario, Pedido, Producto,
                     Resena, UsuarioCustom)


class BaseTestCase(APITestCase):
    def setUp(self):
        self.staff = UsuarioCustom.objects.create_user('admin_test', password='Clave#12345', is_staff=True)
        self.user = UsuarioCustom.objects.create_user('lucas', password='Clave#12345')
        self.otro = UsuarioCustom.objects.create_user('mateo', password='Clave#12345')
        self.cliente = Cliente.objects.create(usuario=self.user, direccion_envio='Calle 1', ciudad='Río Cuarto')
        self.cliente_otro = Cliente.objects.create(usuario=self.otro, direccion_envio='Calle 2', ciudad='Córdoba')

        self.categoria = Categoria.objects.create(nombre='Manga')
        self.editorial = Editorial.objects.create(nombre='Ivrea', pais='Argentina')
        self.autor = Autor.objects.create(nombre='Eiichiro Oda')
        self.producto = Producto.objects.create(
            titulo='One Piece Vol. 1', isbn='111', precio=Decimal('8000.00'),
            categoria=self.categoria, editorial=self.editorial,
        )
        self.producto.autores.add(self.autor)
        Inventario.objects.create(producto=self.producto, cantidad_disponible=10, pasillo='B3')

        self.caro = Producto.objects.create(
            titulo='Libro caro', isbn='222', precio=Decimal('28000.00'),
            categoria=self.categoria, editorial=self.editorial,
        )


class PublicoYDocumentacionTests(BaseTestCase):
    def test_vista_de_bienvenida(self):
        respuesta = self.client.get('/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'La Frikicueva')

    def test_esquema_openapi(self):
        self.assertEqual(self.client.get('/api/schema/').status_code, 200)

    def test_api_navegable(self):
        self.assertEqual(self.client.get('/api/').status_code, 200)


class CatalogoTests(BaseTestCase):
    def test_lectura_publica(self):
        self.assertEqual(self.client.get('/api/productos/').status_code, 200)

    def test_escritura_requiere_login(self):
        respuesta = self.client.post('/api/categorias/', {'nombre': 'Cómic'}, format='json')
        self.assertEqual(respuesta.status_code, 401)

    def test_escritura_prohibida_para_usuarios_comunes(self):
        self.client.force_authenticate(self.user)
        respuesta = self.client.post('/api/categorias/', {'nombre': 'Cómic'}, format='json')
        self.assertEqual(respuesta.status_code, 403)

    def test_staff_puede_crear(self):
        self.client.force_authenticate(self.staff)
        respuesta = self.client.post('/api/categorias/', {'nombre': 'Cómic'}, format='json')
        self.assertEqual(respuesta.status_code, 201)

    def test_anidado_solo_en_list(self):
        listado = self.client.get('/api/productos/')
        self.assertIsInstance(listado.data['results'][0]['categoria'], dict)
        detalle = self.client.get(f'/api/productos/{self.producto.id}/')
        self.assertEqual(detalle.data['categoria'], self.categoria.id)

    def test_paginacion(self):
        respuesta = self.client.get('/api/productos/')
        for clave in ('count', 'next', 'previous', 'results'):
            self.assertIn(clave, respuesta.data)

    def test_busqueda_y_filtros(self):
        self.assertEqual(self.client.get('/api/productos/', {'search': 'One Piece'}).data['count'], 1)
        self.assertEqual(self.client.get('/api/productos/?precio_min=20000').data['count'], 1)
        self.assertEqual(self.client.get('/api/productos/?en_stock=true').data['count'], 1)
        self.assertEqual(self.client.get(f'/api/productos/?categoria={self.categoria.id}').data['count'], 2)

    def test_accion_economicos(self):
        respuesta = self.client.get('/api/productos/economicos/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['count'], 1)

    def test_no_se_borra_categoria_con_productos(self):
        self.client.force_authenticate(self.staff)
        respuesta = self.client.delete(f'/api/categorias/{self.categoria.id}/')
        self.assertEqual(respuesta.status_code, 409)

    def test_bajo_stock_solo_staff(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.get('/api/inventario/bajo_stock/').status_code, 403)
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.get('/api/inventario/bajo_stock/?limite=20').status_code, 200)


class AutenticacionTests(BaseTestCase):
    def test_login_devuelve_token(self):
        respuesta = self.client.post('/api/auth/login/', {'username': 'lucas', 'password': 'Clave#12345'}, format='json')
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('token', respuesta.data)

    def test_token_permite_acceder(self):
        token = self.client.post('/api/auth/login/', {'username': 'lucas', 'password': 'Clave#12345'}, format='json').data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(self.client.get('/api/pedidos/').status_code, 200)

    def test_registro(self):
        respuesta = self.client.post(
            '/api/auth/registro/',
            {'username': 'nuevo_usuario', 'email': 'nuevo@mail.com', 'password': 'UnaClave#Segura2026'},
            format='json',
        )
        self.assertEqual(respuesta.status_code, 201)
        self.assertIn('token', respuesta.data)

    def test_logout_invalida_el_token(self):
        token = self.client.post('/api/auth/login/', {'username': 'lucas', 'password': 'Clave#12345'}, format='json').data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(self.client.post('/api/auth/logout/').status_code, 204)
        self.assertEqual(self.client.get('/api/pedidos/').status_code, 401)


class SesionParaElFrontTests(BaseTestCase):
    def test_login_devuelve_token_y_si_es_staff(self):
        r = self.client.post('/api/auth/login/', {'username': 'admin_test', 'password': 'Clave#12345'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data['token'])
        self.assertTrue(r.data['usuario']['is_staff'])

    def test_login_con_clave_incorrecta_da_400(self):
        r = self.client.post('/api/auth/login/', {'username': 'lucas', 'password': 'mal'}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_me_requiere_token_y_devuelve_usuario(self):
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 401)
        token = self.client.post('/api/auth/login/', {'username': 'lucas', 'password': 'Clave#12345'}, format='json').data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        r = self.client.get('/api/auth/me/')
        self.assertEqual((r.status_code, r.data['username'], r.data['is_staff']), (200, 'lucas', False))

    def test_producto_acepta_imagen_url_opcional(self):
        token = self.client.post('/api/auth/login/', {'username': 'admin_test', 'password': 'Clave#12345'}, format='json').data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        datos = {'titulo': 'Nuevo', 'isbn': '999', 'precio': '100.00', 'categoria': self.categoria.id,
                 'editorial': self.editorial.id, 'autores': [self.autor.id], 'imagen_url': 'https://ejemplo.com/p.jpg'}
        r = self.client.post('/api/productos/', datos, format='json')
        self.assertEqual((r.status_code, r.data['imagen_url']), (201, 'https://ejemplo.com/p.jpg'))

    def test_inventario_se_filtra_por_producto(self):
        r = self.client.get(f'/api/inventario/?producto={self.producto.id}')
        self.assertEqual(r.data['count'], 1)


class PedidosTests(BaseTestCase):
    def test_pedidos_requieren_login(self):
        self.assertEqual(self.client.get('/api/pedidos/').status_code, 401)
        self.assertEqual(self.client.get('/api/clientes/').status_code, 401)

    def test_flujo_de_compra_y_cancelacion(self):
        self.client.force_authenticate(self.user)
        pedido_id = self.client.post('/api/pedidos/', {}, format='json').data['id']

        respuesta = self.client.post(
            '/api/detalles/', {'pedido': pedido_id, 'producto': self.producto.id, 'cantidad': 2}, format='json'
        )
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(Decimal(respuesta.data['precio_unitario']), Decimal('8000.00'))

        pedido = Pedido.objects.get(pk=pedido_id)
        self.assertEqual(pedido.total, Decimal('16000.00'))
        self.assertEqual(Inventario.objects.get(producto=self.producto).cantidad_disponible, 8)

        respuesta = self.client.post(f'/api/pedidos/{pedido_id}/cancelar/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Pedido.objects.get(pk=pedido_id).estado, 'C')
        self.assertEqual(Inventario.objects.get(producto=self.producto).cantidad_disponible, 10)

        # Ya cancelado: no se puede volver a cancelar
        self.assertEqual(self.client.post(f'/api/pedidos/{pedido_id}/cancelar/').status_code, 400)

    def test_stock_insuficiente(self):
        self.client.force_authenticate(self.user)
        pedido_id = self.client.post('/api/pedidos/', {}, format='json').data['id']
        respuesta = self.client.post(
            '/api/detalles/', {'pedido': pedido_id, 'producto': self.producto.id, 'cantidad': 99}, format='json'
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_un_cliente_no_ve_pedidos_ajenos(self):
        pedido = Pedido.objects.create(cliente=self.cliente)
        self.client.force_authenticate(self.otro)
        self.assertEqual(self.client.get('/api/pedidos/').data['count'], 0)
        self.assertEqual(self.client.get(f'/api/pedidos/{pedido.id}/').status_code, 404)

    def test_pedidos_anidado_solo_en_list(self):
        pedido = Pedido.objects.create(cliente=self.cliente)
        self.client.force_authenticate(self.user)
        listado = self.client.get('/api/pedidos/')
        self.assertIsInstance(listado.data['results'][0]['cliente'], dict)
        detalle = self.client.get(f'/api/pedidos/{pedido.id}/')
        self.assertEqual(detalle.data['cliente'], self.cliente.id)

    def test_enviar_solo_staff(self):
        pedido = Pedido.objects.create(cliente=self.cliente)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.post(f'/api/pedidos/{pedido.id}/enviar/').status_code, 403)
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.post(f'/api/pedidos/{pedido.id}/enviar/').status_code, 200)
        self.assertEqual(Pedido.objects.get(pk=pedido.id).estado, 'E')


class ResenasTests(BaseTestCase):
    def test_una_resena_por_producto_y_cliente(self):
        self.client.force_authenticate(self.user)
        datos = {'producto': self.producto.id, 'puntaje': 5, 'comentario': 'Excelente'}
        self.assertEqual(self.client.post('/api/resenas/', datos, format='json').status_code, 201)
        self.assertEqual(self.client.post('/api/resenas/', datos, format='json').status_code, 400)
        self.assertEqual(Resena.objects.count(), 1)

    def test_solo_el_dueno_edita_su_resena(self):
        resena = Resena.objects.create(producto=self.producto, cliente=self.cliente, puntaje=4, comentario='Bien')
        self.client.force_authenticate(self.otro)
        respuesta = self.client.patch(f'/api/resenas/{resena.id}/', {'puntaje': 1}, format='json')
        self.assertEqual(respuesta.status_code, 403)

    def test_resenas_de_un_producto(self):
        Resena.objects.create(producto=self.producto, cliente=self.cliente, puntaje=4, comentario='Bien')
        respuesta = self.client.get(f'/api/productos/{self.producto.id}/resenas/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['count'], 1)
