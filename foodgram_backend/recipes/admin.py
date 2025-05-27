from django.contrib import admin

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Регистрация тегов."""

    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Регистрация ингредиентов."""

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    """Отображение рецептов в админке."""

    model = RecipeIngredient
    extra = 1


class FavoritesInline(admin.TabularInline):
    """Отображение избранного в админке."""

    model = Favorite
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Регистрация рецептов."""

    inlines = (RecipeIngredientInline, FavoritesInline,)
    list_display = ('name', 'author')
    readonly_fields = ('favorite_count',)
    fields = (
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
        'tags',
        'favorite_count'
    )
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name',)

    @admin.display(description='Добавлен в избранное')
    def favorite_count(self, obj):
        """Количество в избранном."""
        return obj.favorites.count()


@admin.register(Favorite, ShoppingCart)
class FavoriteShopAdmin(admin.ModelAdmin):
    """Регистрация избранного и корзины."""

    list_display = ('recipe', 'user')
    search_fields = ('recipe', 'user')
    list_filter = ('recipe', 'user')
