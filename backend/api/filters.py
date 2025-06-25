from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag, User


class NameFilterSet(FilterSet):
    """Фильтр для названия ингредиентов."""

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтрация рецептов."""

    author = filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        field_name='author__username',
        label='Автор'
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        label='Тэги'
    )
    is_favorited = filters.BooleanFilter(
        method='check_is_favorited',
        label='В избранном'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='check_in_cartshop',
        label='В корзине покупок'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def check_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def check_in_cartshop(self, queryset, name, value):
        user = self.request.user
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset
