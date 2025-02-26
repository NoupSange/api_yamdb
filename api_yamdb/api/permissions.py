from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает редактирование и удаление контента администратору.
    Чтение доступно всем.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and request.user.is_admin
        )


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
            or request.user.is_moderator
            or request.user.is_admin
            or obj.author == request.user
        )


class IsAdmin(permissions.BasePermission):
    """Разрешает действия только Администратору."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
