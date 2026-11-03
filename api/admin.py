from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (Autor, Categoria, Cliente, DetallePedido, Editorial, Inventario,
                     Pedido, Producto, Resena, UsuarioCustom)


@admin.register(UsuarioCustom)
class UsuarioCustomAdmin(UserAdmin):
    # Añadimos el campo personalizado de teléfono al panel de usuario
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Contacto', {'fields': ('telefono',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Contacto', {'fields': ('telefono',)}),
    )
    list_display = ('username', 'email', 'telefono', 'is_staff')
    search_fields = ('username', 'email', 'telefono')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(Editorial)
class EditorialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pais')
    list_filter = ('pais',)
    search_fields = ('nombre', 'pais')
    ordering = ('nombre',)


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    ordering = ('nombre',)


class InventarioInline(admin.StackedInline):
    model = Inventario
    extra = 0


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'isbn', 'precio', 'categoria', 'editorial')
    list_filter = ('categoria', 'editorial')
    search_fields = ('titulo', 'isbn')
    ordering = ('titulo',)
    filter_horizontal = ('autores',)
    inlines = [InventarioInline]


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad_disponible', 'pasillo')
    list_filter = ('pasillo',)
    search_fields = ('producto__titulo', 'pasillo')
    ordering = ('cantidad_disponible',)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'ciudad', 'direccion_envio')
    list_filter = ('ciudad',)
    search_fields = ('usuario__username', 'usuario__email', 'ciudad')


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_creacion', 'estado', 'total')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('cliente__usuario__username', 'cliente__usuario__email')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('total',)
    inlines = [DetallePedidoInline]
    actions = ['marcar_enviados']

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        # Si se editan líneas desde el admin, se recalcula el total del pedido
        form.instance.recalcular_total()

    @admin.action(description='Marcar pedidos pendientes como enviados')
    def marcar_enviados(self, request, queryset):
        cantidad = queryset.filter(estado='P').update(estado='E')
        self.message_user(request, f'{cantidad} pedido(s) marcado(s) como enviado(s).')


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario')
    search_fields = ('producto__titulo',)


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cliente', 'puntaje')
    list_filter = ('puntaje',)
    search_fields = ('producto__titulo', 'cliente__usuario__username', 'comentario')
