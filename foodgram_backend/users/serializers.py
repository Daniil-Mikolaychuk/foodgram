from drf_extra_fields.fields import Base64ImageField
from django.db.models import F
from rest_framework import serializers
from rest_framework.validators import ValidationError, UniqueTogetherValidator

from users.models import User, Subscriptions


class UserSerializer(serializers.ModelSerializer):
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
        return Subscriptions.objects.filter(user=user, author=obj).exists()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватарки"""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)