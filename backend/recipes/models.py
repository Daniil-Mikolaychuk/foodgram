from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, validate_email
from django.db import models

from recipes.constants import (NAME_MAX_LENGTH, STR_SYMBOL_LIMIT,
                               VALID_CHARACTERS_USERNAME)


class User(AbstractUser):
    """Пользователь."""

    email = models.EmailField(
        'E-mail адрес',
        validators=[validate_email],
        unique=True
    )
    username = models.CharField(
        'Логин',
        max_length=NAME_MAX_LENGTH,
        unique=True,
        help_text="Не более 150 символов. Только буквы, цифры и @/./+/-/_.",
        validators=[
            RegexValidator(
                regex=VALID_CHARACTERS_USERNAME,
                message='Имя пользователя должно '
                        'соответствовать шаблону.',
                code='invalid_username')
        ]
    )
    first_name = models.CharField('Имя', max_length=NAME_MAX_LENGTH)
    last_name = models.CharField('Фамилия', max_length=NAME_MAX_LENGTH)
    avatar = models.ImageField(
        upload_to='users/',
        null=True,
        blank=True,
        verbose_name='Аватар',
        default=None
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class Subscription(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='following'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='follower'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('author',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='followers_unique'
            )
        ]

    def __str__(self):
        return self.author.username


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
        db_index=True,
        unique=True
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
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=NAME_MAX_LENGTH,
        unique=True,
        null=False,
        db_index=True
    )
    image = models.ImageField(
        'Изображение блюда',
        upload_to='recipes/images/',
        null=False
    )
    text = models.TextField(
        'Описание рецепта'
    )
    published_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        through='RecipeIngredient'
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
        null=False
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ('-published_date',)

    def __str__(self):
        return self.name[:STR_SYMBOL_LIMIT]


class RecipeIngredient(models.Model):
    """Ингридиенты для использования в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Название рецепта',
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент рецепта',
        related_name='recipe_ingredients',
    )
    amount = models.IntegerField(
        'Количество'
    )

    class Meta:
        verbose_name = 'Ингридиент для рецепта'
        verbose_name_plural = 'Ингридиенты для рецепта'
        ordering = ('recipe',)
        db_table = 'recipes_recipe_ingredient'

    def __str__(self):
        return f'{self.ingredient.name} {self.recipe.name}'


class Favorite(models.Model):
    """Избранное."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Любимые рецепты'
        verbose_name_plural = 'Любимые рецепты'
        default_related_name = 'favorites'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='user_favorite'
            )
        ]

    def __str__(self):
        return f'{self.recipe.name[:STR_SYMBOL_LIMIT]} визбранном {self.user}'


class ShoppingCart(models.Model):
    """Модель списка рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Покупатель',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        default_related_name = 'shopping_cart'
        ordering = ('user',)

    def __str__(self):
        return f'{self.recipe.name[:STR_SYMBOL_LIMIT]} в корзине у {self.user}'
