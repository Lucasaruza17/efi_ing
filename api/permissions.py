from rest_framework import permissions


class EsStaffOSoloLectura(permissions.BasePermission):
    """Catálogo: cualquiera puede leer; solo el staff puede crear, editar o borrar."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class EsDuenoOStaff(permissions.BasePermission):
    """Para objetos con atributo `cliente` (ej. Reseña): solo su dueño o el staff pueden modificarlos."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user.is_staff or obj.cliente.usuario_id == request.user.id)
