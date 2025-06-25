from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet,
                    ShoppingCartViewSet, SubscribeViewSet,
                    SubscriptionsListViewSet, TagViewSet, UserProfileViewSet)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('users', UserProfileViewSet, basename='users')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

user_urlpatterns = [
    path(
        '<int:user_id>/subscribe/',
        SubscribeViewSet.as_view(
            {'delete': 'destroy',
             'post': 'create'}
        ),
        name='subscribe'
    ),
    path(
        'subscriptions/',
        SubscriptionsListViewSet.as_view({'get': 'list'}),
        name='subscriptionsList'
    )
]

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartViewSet.as_view(
            {
                'delete': 'destroy',
                'post': 'create'
            }
        ),
        name='shopping_cart'
    ),
    path(
        'recipes/download_shopping_cart/',
        ShoppingCartViewSet.as_view(
            {
                'get': 'download_shopping_cart'
            }
        ),
        name='download_shopping_cart'
    ),
    path('users/', include(user_urlpatterns)),
    path('', include(router_v1.urls)),
]
