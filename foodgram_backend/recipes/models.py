from django.db import models
from django.contrib.auth import get_user_model

from recipes.constants import NAME_MAX_LENGTH, STR_SYMBOL_LIMIT

User = get_user_model()

class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        'Название тега',
        max_length=NAME_MAX_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        'Слаг',
        max_length=NAME_MAX_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name[:STR_SYMBOL_LIMIT]


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        'Название ингредиента',
        max_length=NAME_MAX_LENGTH,
        db_index=True
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=NAME_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient')
        ]

    def __str__(self):
        return (
            f'{self.name[:STR_SYMBOL_LIMIT]} '
            f'({self.measurement_unit})'
        )



class Recipe(models.Model):
    """Рецепты."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        'Название рецепта',
        max_length=NAME_MAX_LENGTH,
        db_index=True
    )
    image = models.ImageField(
        'Изображение блюда',
        upload_to='recipes/'
    )
    text = models.TextField(
        'Описание рецепта'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        through='RecipeIngredient'
    )
    cooking_time = models.IntegerField(
        'Время приготовления'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:STR_SYMBOL_LIMIT]


class RecipeIngredient(models.Model):
    """Ингридиенты для использования в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Название рецепта',
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент рецепта',
        related_name='ingredients_recipe'
    )
    amount = models.IntegerField(
        'Количество',
    )

    class Meta:
        verbose_name = 'Ингридиент для рецепта'
        verbose_name_plural = 'Ингридиенты для рецепта'
        ordering = ('recipe',)

    def __str__(self):
        f'Рецепт: {self.recipe.recipe[:STR_SYMBOL_LIMIT]}'


class Favorite(models.Model):
    """Избранное."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Покупатель'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Любимые рецепты'
        verbose_name_plural = 'Любимые рецепты'
        default_related_name = 'favorites' 
        ordering = ('user',)

    def __str__(self):
        return self.recipe[:STR_SYMBOL_LIMIT]


class ShoppingCart(models.Model):
    """Модель списка рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Покупатель'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        default_related_name = 'carts' 
        ordering = ('user',)

    def __str__(self):
        return self.recipe[:STR_SYMBOL_LIMIT]
