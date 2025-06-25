import re
from django.core.exceptions import ValidationError
from .constants import PATTERN_USERNAME


def user_username_validator(username):
    if re.match(PATTERN_USERNAME, username) is None:
        raise ValidationError(
            'В username имеется запрещенный символ!'
        )