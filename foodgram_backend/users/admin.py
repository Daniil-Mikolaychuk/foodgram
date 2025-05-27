from django.contrib import admin

from users.models import User, Subscriptions


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')


@admin.register(Subscriptions)
class SubscriptionAdmin(admin.ModelAdmin):
    """Регистрация модели подписок на авторов."""

    list_display = ('user', 'author')
