from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username
from backend.constants import (LENG_DATA_USER, LENG_EMAIL,
                               LIMITED_NUMBER_OF_CHARACTERS)


class User(AbstractUser):
    """Модель пользователя."""
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Аватар'
    )

    username = models.CharField(
        "username",
        max_length=LENG_DATA_USER,
        unique=True,
        help_text="Не более 150 символов. Только буквы, цифры и @/./+/-/_.",
        validators=[validate_username],
        error_messages={
            "unique": "Пользователь с таким именем уже существует.",
        },
    )

    first_name = models.CharField(
        'Имя',
        max_length=LENG_DATA_USER,
        help_text=LIMITED_NUMBER_OF_CHARACTERS
    )

    last_name = models.CharField(
        'Фамилия',
        max_length=LENG_DATA_USER,
        blank=False,
        null=False,
        help_text=LIMITED_NUMBER_OF_CHARACTERS
    )

    email = models.EmailField(
        'Электронная почта',
        max_length=LENG_EMAIL,
        unique=True,
        blank=False,
        null=False,
        help_text=LIMITED_NUMBER_OF_CHARACTERS
    )

    password = models.CharField(
        'Пароль',
        max_length=LENG_DATA_USER,
        help_text=LIMITED_NUMBER_OF_CHARACTERS,
        blank=False,
        null=False
    )

    REQUIRED_FIELDS = ("username", "first_name", "last_name")
    USERNAME_FIELD = "email"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписчика."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='no_self_follow'
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.author}'