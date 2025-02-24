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
            raise MethodNotAllowed('PUT', detail='Метод PUT не разрешен.')
        return True


class IsAdmin(permissions.BasePermission):
    """Разрешает доступ только администраторам."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )


class IsModerator(permissions.BasePermission):
    """Разрешает доступ модераторам и выше."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.role == 'moderator'
        )


class AuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    """Разрешает:
    - moderator, admin - право удалять и редактировать любые отзывы и
    комментарии.
    - author - создателю объекта разрешено удаление и редактирование
    созданного объекта.
    - остальным только чтение.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                )

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.role == 'admin'
                or obj.author == request.user
                or request.user.role == 'moderator'
                )


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Разрешает чтение всем, а создание, редактирование
    и удаление — только аутентифицированным пользователям.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )


class IsAdminOrOwner(permissions.BasePermission):
    """
    Разрешает чтение и изменение собственной записи любому
    авторизованному пользователю.
    Разрешает чтение и изменение чужих записей только Администратору.
    """

    def has_permission(self, request, view):
        is_auth = request.user.is_authenticated
        if view.action == 'list':
            return is_auth and (
                request.user.role == 'admin'
                or request.user.is_superuser
            )
        return is_auth

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and (
                request.user.role == 'admin'
                or request.user.is_superuser
                or request.user == obj
            )
        )
