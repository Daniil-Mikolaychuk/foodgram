from django.core.validators import RegexValidator

from recipes.constants import VALID_CHARACTERS_USERNAME


def username_validator(value):
    RegexValidator(regex=VALID_CHARACTERS_USERNAME,
                   message='Имя пользователя должно\
                   соответствовать шаблону.',
                   code='invalid_username')
