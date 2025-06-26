from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import NameFilterSet, RecipeFilter
from api.pagination import LimitPagination
from api.permissions import IsAdminAuthorOrReadOnly
from api.serializers import (AvatarSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeCreateSerializer,
                             RecipeReadSerializer, ShoppingCartSerializer,
                             SubscribeSerializer, SubscriptionsSerializer,
                             TagSerializer, UserSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, ShoppingCart, Tag,
                            User)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для получения тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для получения списка ингредиентов и отдельного ингредиента."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = NameFilterSet


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для получения рецепт."""

    queryset = Recipe.objects.all()
    pagination_class = LimitPagination
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminAuthorOrReadOnly
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        """В Избранном."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user
        favorite = Favorite.objects.filter(user=user, recipe=recipe)
        if favorite.exists():
            deleted_count, _ = favorite.delete()
            return Response(
                {'count': deleted_count},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST', 'DELETE'],
        serializer_class=ShoppingCartSerializer,
        permission_classes=(IsAuthenticated,),
        detail=True,
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user
        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                user=user, recipe=recipe
            ).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            cart = ShoppingCart.objects.create(
                user=user,
                recipe=recipe
            )
            serializer = ShoppingCartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            cart = ShoppingCart.objects.filter(
                user=user,
                recipe=recipe
            )
            if not cart.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        cart_recipes = ShoppingCart.objects.filter(user=user)
        ingredients = {}
        for recipe in cart_recipes:
            for ingredient in recipe.recipe.recipe_ingredients.all():
                name = ingredient.ingredient.name
                amount = ingredient.amount
                measurement_unit = ingredient.ingredient.measurement_unit
                if name in ingredients:
                    ingredients[name][0] += amount
                else:
                    ingredients[name] = [amount, measurement_unit]
        carts_list = 'Ваши покупки: '
        for name in ingredients.keys():
            carts_list += (
                f'{name}: '
                f'{ingredients[name][0]} '
                f'{ingredients[name][1]}.'
            )

        response = Response(carts_list, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename="{user}_shopping_list.txt"'
        )
        return response


class UserProfileViewSet(UserViewSet):
    """Получение информации о пользователе."""

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    @action(
        methods=['PUT', 'DELETE'],
        serializer_class=AvatarSerializer,
        permission_classes=(IsAuthenticated,),
        detail=False,
        url_path='me/avatar',
    )
    def avatar(self, request):
        if request.method == 'PUT':
            instance = self.get_instance()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        instance = self.get_instance()
        instance.avatar = None
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        serializer_class=SubscriptionsSerializer,
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        """Список подписок."""
        user = self.request.user
        queryset = User.objects.filter(follower__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        serializer_class=SubscribeSerializer,
        permission_classes=(IsAuthenticated,),
        detail=True,
        url_path='subscribe',
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        follower = request.user.following.filter(author=author)
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data={
                    'user': request.user.id,
                    'author': author.id
                },
                context={
                    'request': request
                },
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if follower is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        follower.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
