from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioCustom, Categoria, Editorial, Autor, Producto, Inventario, Cliente, Pedido, DetallePedido, Resena

@admin.register(UsuarioCustom)
class UsuarioCustomAdmin(UserAdmin):
    # Añadimos el campo personalizado de teléfono al panel de usuario
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Contacto', {'fields': ('telefono',)}),
    )

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'isbn', 'precio', 'categoria', 'editorial')
    list_filter = ('categoria', 'editorial')
    search_fields = ('titulo', 'isbn')
    ordering = ('titulo',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_creacion', 'estado', 'total')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('cliente__usuario__username', 'cliente__usuario__email')
    ordering = ('-fecha_creacion',)

@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cliente', 'puntaje')
    list_filter = ('puntaje',)

# Modelos con visualización estándar
admin.site.register(Categoria)
admin.site.register(Editorial)
admin.site.register(Inventario)
admin.site.register(Cliente)
admin.site.register(DetallePedido)
# Register your models here.
