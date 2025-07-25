from rest_framework import permissions


class IsAdminAuthorOrReadOnly(permissions.BasePermission):
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
            or request.user.is_superuser
        )
