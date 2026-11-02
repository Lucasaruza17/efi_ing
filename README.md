# 🦇 La Frikicueva - Backend (API REST)

**Evaluación Final Integradora (EFI) - Ingeniería de Software 2026**

Este proyecto constituye el backend para "La Frikicueva", una tienda especializada en cómics, mangas y libros de fantasía épica. Desarrollado con Django y Django REST Framework, expone los datos necesarios para ser consumidos por un frontend independiente, cumpliendo con los estándares de autenticación, filtrado y documentación.

## 👥 Equipo de Desarrollo
* Lucas Aruza
* Mateo Gonzalez


## 🗄️ Planificación y Justificación de la Base de Datos

El sistema cuenta con **10 modelos** interrelacionados, diseñados para abarcar la lógica de negocio de una tienda literaria:

1. **UsuarioCustom (Extiende AbstractUser):** Administra la autenticación y añade el campo `telefono` para centralizar el contacto.
2. **Categoria:** Clasifica los productos (Cómic, Manga, Fantasía). Vital para agrupar ítems en el catálogo.
3. **Editorial:** Representa a las empresas editoras (Panini, Ivrea). 
4. **Autor:** Almacena los creadores, escritores o ilustradores. 
5. **Producto:** Modelo central del e-commerce.
   * *Relaciones:* `ForeignKey` a `Categoria` y `Editorial` (1 a N). `ManyToMany` a `Autor` (N a N).
6. **Inventario:** 
   * *Relaciones:* `OneToOne` con `Producto`. Separa la información comercial (precio/título) del depósito físico (stock y pasillo).
7. **Cliente:** 
   * *Relaciones:* `OneToOne` con `UsuarioCustom`. Extiende al usuario para almacenar datos exclusivos de compradores (dirección, ciudad).
8. **Pedido:** 
   * *Relaciones:* `ForeignKey` a `Cliente`. Centraliza la compra registrando fecha, total y estado (Pendiente, Enviado, Cancelado).
9. **DetallePedido:** 
   * *Relaciones:* `ForeignKey` a `Pedido` y `Producto`. Registra la cantidad comprada y "congela" el precio unitario histórico por cuestiones de auditoría.
10. **Reseña:** 
    * *Relaciones:* `ForeignKey` a `Producto` y `Cliente`. Permite a los usuarios dejar calificaciones (1-5) y comentarios.

## 🚀 Instalación y Ejecución (Docker & uv)

El proyecto utiliza `uv` como gestor de paquetes dentro de un entorno Dockerizado.

**1. Levantar los contenedores:**
```bash
docker-compose up --build
```

**2. Inicializar base de datos y cargar catalogo:
En otra terminal, ejecuta las migraciones, crea tu administrador y puebla la base de datos:**
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python populate.py
```
**Accesos del Sistema**
**Vista de Bienvenida: http://localhost:8000/**

**API Navegable: http://localhost:8000/api/**

**Swagger (Documentación): http://localhost:8000/api/docs/swagger/**

**Panel de Administración: http://localhost:8000/admin/**
**Capturas**

