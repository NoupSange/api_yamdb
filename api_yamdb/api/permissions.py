from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает редактирование и удаление контента администратору и суперюзеру.
    Чтение доступно всем.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and (
                request.user.role == 'admin' or request.user.is_superuser
            )
        )


class IsMethodPutAllowed(permissions.BasePermission):
    """Запрещает метод PUT."""

    def has_permission(self, request, view):
        if request.method == 'PUT':
            raise MethodNotAllowed('PUT')
        return True


class AuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает:
    - moderator, admin - право удалять и редактировать любые отзывы и
    комментарии.
    - author - создателю объекта разрешено удаление и редактирование
    созданного объекта.
    - остальным только чтение.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.role in ('admin', 'moderator')
            or obj.author == request.user
        )


class IsAdminOrOwner(permissions.BasePermission):
    """
    Разрешает чтение и изменение собственной записи любому
    авторизованному пользователю.
    Разрешает чтение и изменение чужих записей только Администратору.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role == 'admin' or request.user.is_superuser:
            return True

        if view.action == 'destroy':
            if view.kwargs.get('pk') == 'me':
                raise MethodNotAllowed('DELETE')
            return False

        if view.action not in ('retrieve', 'partial_update'):
            return False

        return True

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and (
                request.user.role == 'admin'
                or request.user.is_superuser
                or view.kwargs.get('pk') == 'me'
            )
        )
