"""Carga datos de ejemplo para La Frikicueva.

Uso (se puede ejecutar varias veces sin duplicar datos):
    python populate.py
    docker compose exec web python populate.py

Crea además un cliente de prueba:  usuario `cliente_demo` / contraseña `demo1234`
"""
import os

import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import (Autor, Categoria, Cliente, DetallePedido, Editorial,  # noqa: E402
                        Inventario, Pedido, Producto, Resena, UsuarioCustom)


def poblar():
    print("Creando datos para La Frikicueva...")

    # Categorías
    cat_comic, _ = Categoria.objects.get_or_create(nombre="Cómic", defaults={"descripcion": "Cómics de superhéroes y occidentales."})
    cat_manga, _ = Categoria.objects.get_or_create(nombre="Manga", defaults={"descripcion": "Historietas de origen japonés."})
    cat_libro, _ = Categoria.objects.get_or_create(nombre="Fantasía Épica", defaults={"descripcion": "Novelas de fantasía y ciencia ficción."})

    # Editoriales
    ed_panini, _ = Editorial.objects.get_or_create(nombre="Panini Comics", defaults={"pais": "Italia"})
    ed_ivrea, _ = Editorial.objects.get_or_create(nombre="Ivrea", defaults={"pais": "Argentina"})
    ed_minotauro, _ = Editorial.objects.get_or_create(nombre="Minotauro", defaults={"pais": "España"})

    # Autores
    aut_stan, _ = Autor.objects.get_or_create(nombre="Stan Lee", defaults={"biografia": "Creador de Spider-Man, X-Men y más."})
    aut_oda, _ = Autor.objects.get_or_create(nombre="Eiichiro Oda", defaults={"biografia": "Mangaka creador de One Piece."})
    aut_tolkien, _ = Autor.objects.get_or_create(nombre="J.R.R. Tolkien", defaults={"biografia": "Autor de El Señor de los Anillos."})
    aut_miura, _ = Autor.objects.get_or_create(nombre="Kentaro Miura", defaults={"biografia": "Mangaka creador de Berserk."})
    aut_toriyama, _ = Autor.objects.get_or_create(nombre="Akira Toriyama", defaults={"biografia": "Mangaka creador de Dragon Ball."})

    # (título, isbn, precio, categoría, editorial, autor, stock, pasillo)
    catalogo = [
        ("Spider-Man: La Última Cacería de Kraven", "978-84-1101-000-1", 15500, cat_comic, ed_panini, aut_stan, 10, "A1"),
        ("One Piece Vol. 1: Romance Dawn", "978-84-1101-000-2", 8000, cat_manga, ed_ivrea, aut_oda, 25, "B3"),
        ("El Señor de los Anillos: La Comunidad del Anillo", "978-84-450-0066-3", 28000, cat_libro, ed_minotauro, aut_tolkien, 5, "C1"),
        ("Berserk Vol. 1", "978-84-1101-000-4", 9500, cat_manga, ed_ivrea, aut_miura, 12, "B1"),
        ("Dragon Ball Vol. 1", "978-84-1101-000-5", 7200, cat_manga, ed_ivrea, aut_toriyama, 30, "B2"),
        ("X-Men: Días del Futuro Pasado", "978-84-1101-000-6", 18900, cat_comic, ed_panini, aut_stan, 3, "A2"),
    ]
    productos = []
    for titulo, isbn, precio, cat, ed, autor, stock, pasillo in catalogo:
        producto, creado = Producto.objects.get_or_create(
            isbn=isbn,
            defaults={"titulo": titulo, "precio": precio, "categoria": cat, "editorial": ed},
        )
        if creado:
            producto.autores.add(autor)
            Inventario.objects.create(producto=producto, cantidad_disponible=stock, pasillo=pasillo)
        productos.append(producto)

    # Cliente de prueba con un pedido y una reseña
    usuario, creado = UsuarioCustom.objects.get_or_create(
        username="cliente_demo", defaults={"email": "demo@frikicueva.com", "telefono": "3584000000"}
    )
    if creado:
        usuario.set_password("demo1234")
        usuario.save()
    cliente, _ = Cliente.objects.get_or_create(
        usuario=usuario, defaults={"direccion_envio": "Av. Sabattini 123", "ciudad": "Río Cuarto"}
    )

    if not cliente.pedidos.exists():
        pedido = Pedido.objects.create(cliente=cliente)
        for producto, cantidad in ((productos[1], 2), (productos[3], 1)):
            DetallePedido.objects.create(
                pedido=pedido, producto=producto, cantidad=cantidad, precio_unitario=producto.precio
            )
            inv = producto.inventario
            inv.cantidad_disponible -= cantidad
            inv.save()
        pedido.recalcular_total()

    Resena.objects.get_or_create(
        producto=productos[1], cliente=cliente,
        defaults={"puntaje": 5, "comentario": "Un clásico, excelente edición."},
    )

    print("¡Base de datos poblada con éxito!")
    print("Cliente de prueba -> usuario: cliente_demo / contraseña: demo1234")


if __name__ == '__main__':
    poblar()
