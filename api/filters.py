from django.db.models import Q
from django_filters import rest_framework as df

from .models import Producto


class ProductoFilter(df.FilterSet):
    precio_min = df.NumberFilter(field_name='precio', lookup_expr='gte')
    precio_max = df.NumberFilter(field_name='precio', lookup_expr='lte')
    autor = df.NumberFilter(field_name='autores__id')
    en_stock = df.BooleanFilter(method='filtrar_en_stock')

    class Meta:
        model = Producto
        fields = ['categoria', 'editorial']

    def filtrar_en_stock(self, queryset, name, value):
        if value:
            return queryset.filter(inventario__cantidad_disponible__gt=0)
        return queryset.filter(Q(inventario__isnull=True) | Q(inventario__cantidad_disponible=0))
