from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Класс прав пользователя."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Проверка, является ли пользователь - автором."""
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Класс прав пользователя."""

    def has_permission(self, request, view):
        """Проверка, является ли пользователь - админ."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff)
