from drf_extra_fields.fields import Base64ImageField
from django.db.models import F
from rest_framework import serializers
from rest_framework.validators import ValidationError, UniqueTogetherValidator

from recipes.models import (Ingredient, Recipe, RecipeIngredient,
                            Tag, Favorite)
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = '__all__'


class IngredintListSerializer(serializers.Serializer):
    """Сериализатор для ингредиентов при создании рецепта."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit.name'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_amount(self, value):
        """Валидация количества ингредиента."""
        if value <= 0:
            raise ValidationError(
                'Отсутствует ингредиент!'
            )
        return value


class RecipeForUserSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов эндпоинта подписок."""

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )
        read_only_fields = '__all__',


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра списка рецептов или рецепта."""

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )
        read_only_fields = (
            '__all__',
        )

    def get_ingredients(self, obj):
        """Получение поля ингредиентов."""
        ingrediens = obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )
        return ingrediens

    def get_is_favorited(self, obj):
        """Получение поля в избранном ли товар."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.fav_recipes.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Получение поля в корзине ли товар."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.cart.filter(recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    image = Base64ImageField()
    ingredients = IngredientCreateSerializer(many=True,)
    cooking_time = serializers.IntegerField(
        min_value=1, max_value=222
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'ingredients',
            'name', 'image', 'text', 'cooking_time',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'ingredients')
            )
        ]

    def validate(self, attrs):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        if not tags or not ingredients:
            raise ValidationError('Отсутствуют обязательные поля!')
        ingredients = [
            ingredient['id'] for ingredient in ingredients
        ]
        if len(ingredients) != len(set(ingredients)):
            raise ValidationError(
                'Нельзя указывать одинаковые ингредиенты!'
            )
        if len(tags) != len(set(tags)):
            raise ValidationError(
                'Нельзя указывать одинаковые теги!'
            )
        if not self.initial_data.get('text'):
            raise ValidationError(
                'Нельзя создать рецепт без текста!'
            )
        return super().validate(attrs)

    def create(self, validated_data):
        """Функция создания рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredients=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount')
            )
        return recipe

    def update(self, instance, validated_data):
        """Функция изменения рецепта."""
        ingredients = validated_data.get('ingredients')
        instance.tags.set(validated_data.get('tags'))
        instance.image = validated_data.get('image')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        if ingredients:
            instance.ingredients.clear()
            create_relation_ingredient_and_value(
                ingredients_list=ingredients,
                recipe=instance
            )
        instance.save()
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов."""

    id = serializers.IntegerField(source='recipe.id')
    name = serializers.CharField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image')
    cooking_time = serializers.IntegerField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('recipe', 'user')


