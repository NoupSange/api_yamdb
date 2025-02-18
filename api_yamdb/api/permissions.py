from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Разрешает доступ только администраторам."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )


class IsModerator(permissions.BasePermission):
    """Разрешает доступ модераторам и выше."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_moderator


class AuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает редактирование и удаление контента
    его автору, модератору или администратору.
    Чтение доступно всем.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Разрешает чтение всем, а создание, редактирование
    и удаление — только аутентифицированным пользователям.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or request.user.is_authenticated
