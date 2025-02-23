from rest_framework import permissions


class AllowAny(permissions.BasePermission):
    """Разрешает доступ всем пользователям."""
    pass


class IsAdmin(permissions.BasePermission):
    """Разрешает доступ только пользователю с ролью администратора."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == "admin" or request.user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        return True


class AdminOrReadOnly(permissions.BasePermission):
    """Разрешает просмотр всем, изменения только админу."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.role == "admin" or request.user.is_superuser
        )


class OwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает просмотр всем.
    Разрешает добавить новый
    объект аутентифицированному пользователю.
    Разрешает доступ к конкретным объектам только авторму,
    модератору или админу.
    """
    def has_permission(self, request, view):
        if (request.method in permissions.SAFE_METHODS
           and request.user.is_authenticated):
            return True
        if request.method == 'PATCH':
            return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
            return (
                obj.author == request.user
                or request.user.role == "moderator"
                or request.user.role == "admin"
            )
        except AttributeError:
            pass
        return True

############################ все ниже не нужно
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


# class IsAdmin(permissions.BasePermission):
#     """Разрешает доступ только администраторам."""

#     def has_permission(self, request, view):
#         return request.user.is_authenticated and (
#             request.user.is_admin or request.user.is_superuser
#         )


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
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

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

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and (
                request.user.role == 'admin'
                or request.user.is_superuser
                or request.user == obj
            )
        )
