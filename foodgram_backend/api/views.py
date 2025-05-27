from rest_framework import permissions, viewsets

from recipes.models import Tag, Favorite, Ingredient, Recipe, ShoppingCart
from api.serializers import TagSerializer, IngredientSerializer
from api.permissions import (IsOwnerOrReadOnly, IsAdminOrReadOnly)
from api.filters import NameFilterSet
from rest_framework.serializers import ModelSerializer, SerializerMethodField


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для получения тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для получения списка ингредиентов и отдельного ингредиента."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = NameFilterSet
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


# class CustomDjoserUserViewSet(DjoserUserViewSet):
#     """Пользователь."""

#     @action(
#         detail=False, methods=["GET"], permission_classes=[IsAuthenticated]
#     )
#     def me(self, request):
#         serializer = self.get_serializer(request.user)
#         return Response(serializer.data)


# class UserSubscribeView(APIView):
#     """Подписка на пользователя."""

#     permission_classes = (IsAdminAuthorOrReadOnly,)

#     def post(self, request, user_id):
#         author = get_object_or_404(User, id=user_id)
#         serializer = UserSubscribeSerializer(
#             data={"user": request.user.id, "author": author.id},
#             context={"request": request},
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def delete(self, request, user_id):
#         author = get_object_or_404(User, id=user_id)
#         follower = request.user.follower.filter(author=author)
#         if not follower:
#             return Response(
#                 {"error": "Нет подписки на этого пользователя"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         follower.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class UserSubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     """Получение списка всех подписок на пользователей."""

#     serializer_class = UserSubscribeRepresentSerializer

#     def get_queryset(self):
#         return User.objects.filter(following__user=self.request.user)
