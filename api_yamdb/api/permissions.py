from rest_framework import permissions


class IsAdminSuperUserOrReadOnly(permissions.BasePermission):
    """
    Разрешает редактирование и удаление контента администратору и суперюзеру.
    Чтение доступно всем.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
            or request.user.is_superuser
        )


class IsMethodPutAllowed(permissions.BasePermission):
    """Запрещает метод PUT."""

    def has_permission(self, request, view):
        return request.method != 'PUT'
