from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag, User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Регистрация модели пользователей."""

    list_display = (
        'id', 'username', 'email',
        'recipes_amount', 'subscribers_amount'
    )
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')
    list_display_links = ('username',)

    @admin.display(description='Количество рецептов')
    def recipes_amount(self, obj):
        return obj.recipes.count()

    @admin.display(description='Количество подписчиков')
    def subscribers_amount(self, obj):
        return obj.following.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Регистрация модели подписок на авторов."""

    list_display = ('user', 'author')
    list_filter = ('user', 'author')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Регистрация тегов."""

    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    list_display_links = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Регистрация ингредиентов."""

    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    """Отображение рецептов в админке."""

    model = RecipeIngredient
    extra = 1
    min_num = 1


class FavoritesInline(admin.TabularInline):
    """Отображение избранного в админке."""

    model = Favorite
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Регистрация рецептов."""

    inlines = (RecipeIngredientInline, FavoritesInline,)
    list_display = ('id', 'name', 'author', 'favorite_count')
    readonly_fields = ('favorite_count',)
    list_filter = ('name', 'author', 'tags')
    list_display_links = ('name',)
    search_fields = ('name',)

    @admin.display(description='Добавлено в избранное')
    def favorite_count(self, obj):
        """Количество в избранном."""
        return obj.favorites.count()


@admin.register(Favorite, ShoppingCart)
class FavoriteShopAdmin(admin.ModelAdmin):
    """Регистрация избранного и корзины."""

    list_display = ('id', 'recipe', 'user')
    search_fields = ('recipe', 'user')
    list_filter = ('recipe', 'user')
