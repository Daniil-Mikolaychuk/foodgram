from django.core.validators import MinLengthValidator, MinValueValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from recipes.constants import (MAX_COOKS_TIME, MIN_COOKS_TIME, NAME_MAX_LENGTH,
                               VALID_CHARACTERS_USERNAME)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag, User)


class UserSerializer(UserSerializer):
    """Сериализатор для user."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'avatar',
            'first_name', 'last_name', 'is_subscribed'
        )
        read_only_fields = 'is_subscribed',

    def get_is_subscribed(self, obj):
        """Проверка, если ли подписка на пользователя."""
        user = self.context['request'].user
        if user.is_anonymous or user == obj:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериалайзер для регистрации пользователей."""

    first_name = serializers.CharField(
        max_length=NAME_MAX_LENGTH,
        validators=[MinLengthValidator(2)],
        required=True,
    )
    last_name = serializers.CharField(
        max_length=NAME_MAX_LENGTH,
        validators=[MinLengthValidator(2)],
        required=True,
    )
    username = serializers.RegexField(
        regex=VALID_CHARACTERS_USERNAME,
        validators=[MinLengthValidator(2)],
        max_length=NAME_MAX_LENGTH
    )
    password = serializers.CharField(
        validators=[MinLengthValidator(8)],
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'id',
            'password',
        )

        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email'],
                message='Username and email должны быть уникальны!',
            )
        ]


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериалайзер для работы с подписками."""

    class Meta:
        model = Subscription
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя',
            )
        ]

    def validate(self, data):
        """Проверка подписи на себя."""
        user = self.context.get('request').user
        if user == data.get('author'):
            raise ValidationError('Нельзя подписаться на самого себя!')
        return data


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор списка подписок."""

    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )

    def get_recipes(self, obj):
        """Получение рецептов автора."""
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None and recipes_limit.isdigit():
            limit = int(recipes_limit)
            recipes = recipes[:limit]
        return RecipeShortSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        """Получение рецептов автора."""
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения из рецепта ингредиентов."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )
    name = serializers.ReadOnlyField(source='ingredient.name')

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class IngredientAddRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления в рецепт ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        validators=(MinValueValidator(1),)
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        return 'ShortCartSerializer'(
            instance.recipe,
            context={'request': request}
        ).data


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра списка рецептов или рецепта."""

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='recipe_ingredients',
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        """Получение поля в избранном ли товар."""
        user = self.context.get('request').user
        return (
            not user.is_anonymous
            and obj.favorites.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Получение поля в корзине ли товар."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return (
            not user.is_anonymous
            and obj.shopping_cart.filter(user=user).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    image = Base64ImageField()
    ingredients = IngredientAddRecipeSerializer(many=True)
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKS_TIME, max_value=MAX_COOKS_TIME
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'ingredients', 'author',
            'name', 'image', 'text', 'cooking_time',
        )
        read_only_fields = ('author',)
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'ingredients')
            )
        ]

    def validate(self, data):
        """Валидация."""
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        ingredients_list = []
        for ingredient in ingredients:
            try:
                ingredient = Ingredient.objects.get(id=ingredient['id'])
            except Ingredient.DoesNotExist:
                raise ValidationError(
                    'Такого ингредиента нет!'
                )
            if ingredient in ingredients_list:
                raise ValidationError(
                    'Ингредиенты не должны повторятся!'
                )
            ingredients_list.append(ingredient)
        if len(tags) != len(set(tags)):
            raise ValidationError(
                'Проверьте теги на дубликаты!'
            )
        if not data.get('text'):
            raise ValidationError(
                'Нельзя создать рецепты без текста!'
            )
        return data

    def add_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient.get('id'),
                    amount=ingredient.get('amount'),
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        user = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = super().update(instance, validated_data)
        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        if ingredients:
            recipe.ingredients.clear()
            self.add_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance,
                                    context=context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов в подписках."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в избранные."""

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже находится в избранном',
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже находится в покупках',
            )
        ]
