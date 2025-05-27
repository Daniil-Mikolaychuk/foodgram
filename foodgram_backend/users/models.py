from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, validate_email

from recipes.constants import NAME_MAX_LENGTH, VALID_CHARACTERS_USERNAME


class User(AbstractUser):
    """Пользователь."""

    username = models.CharField(
        'Логин',
        max_length=NAME_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=VALID_CHARACTERS_USERNAME,
                message='Имя пользователя должно\
                соответствовать шаблону.',
                code='invalid_username')
        ]
    )
    first_name = models.CharField("Имя", max_length=NAME_MAX_LENGTH)
    last_name = models.CharField("Фамилия", max_length=NAME_MAX_LENGTH)
    password = models.CharField(
        'Пароль',
        max_length=NAME_MAX_LENGTH)

    email = models.EmailField(
        'E-mail адрес',
        validators=[validate_email],
        unique=True
    )
    avatar = models.ImageField(
        upload_to='users/images/',
        blank=True,
        null=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class Subscriptions(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')

    class Meta:
        default_related_name = 'follower' 
        ordering = ('author',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='followers_unique')]

    def __str__(self):
        return f'{self.user} подписчик автора - {self.author}'
