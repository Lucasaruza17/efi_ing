import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Categoria, Editorial, Autor, Producto, Inventario

def poblar():
    print("Creando datos para La Frikicueva...")

    # Categorías
    cat_comic, _ = Categoria.objects.get_or_create(nombre="Cómic", descripcion="Cómics de superhéroes y occidentales.")
    cat_manga, _ = Categoria.objects.get_or_create(nombre="Manga", descripcion="Historietas de origen japonés.")
    cat_libro, _ = Categoria.objects.get_or_create(nombre="Fantasía Épica", descripcion="Novelas de fantasía y ciencia ficción.")

    # Editoriales
    ed_panini, _ = Editorial.objects.get_or_create(nombre="Panini Comics", pais="Italia")
    ed_ivrea, _ = Editorial.objects.get_or_create(nombre="Ivrea", pais="Argentina")
    ed_minotauro, _ = Editorial.objects.get_or_create(nombre="Minotauro", pais="España")

    # Autores
    aut_stan, _ = Autor.objects.get_or_create(nombre="Stan Lee", biografia="Creador de Spider-Man, X-Men y más.")
    aut_oda, _ = Autor.objects.get_or_create(nombre="Eiichiro Oda", biografia="Mangaka creador de One Piece.")
    aut_tolkien, _ = Autor.objects.get_or_create(nombre="J.R.R. Tolkien", biografia="Autor de El Señor de los Anillos.")

    # Productos e Inventario
    p1, creado1 = Producto.objects.get_or_create(
        titulo="Spider-Man: La Última Cacería de Kraven", isbn="978-84-1101-000-1",
        precio=15500.00, categoria=cat_comic, editorial=ed_panini
    )
    if creado1:
        p1.autores.add(aut_stan)
        Inventario.objects.create(producto=p1, cantidad_disponible=10, pasillo="A1")

    p2, creado2 = Producto.objects.get_or_create(
        titulo="One Piece Vol. 1: Romance Dawn", isbn="978-84-1101-000-2",
        precio=8000.00, categoria=cat_manga, editorial=ed_ivrea
    )
    if creado2:
        p2.autores.add(aut_oda)
        Inventario.objects.create(producto=p2, cantidad_disponible=25, pasillo="B3")

    p3, creado3 = Producto.objects.get_or_create(
        titulo="El Señor de los Anillos: La Comunidad del Anillo", isbn="978-84-450-0066-3",
        precio=28000.00, categoria=cat_libro, editorial=ed_minotauro
    )
    if creado3:
        p3.autores.add(aut_tolkien)
        Inventario.objects.create(producto=p3, cantidad_disponible=5, pasillo="C1")

    print("¡Base de datos poblada con éxito!")

if __name__ == '__main__':
    poblar()