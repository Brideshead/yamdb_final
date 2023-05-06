import re

from django.core.exceptions import ValidationError


def validate_username(value):
    """Проверка валидности имени."""
    if value == 'me':
        raise ValidationError(
            'Имя пользователя не может быть <me>.',
            params={'value': value},
        )
    if re.search(r'^[a-zA-Z][\w+.@+-]{1,150}$', value) is None:
        raise ValidationError(
            'Имя пользователя содержит не допустимые символы.',
            params={'value': value},
        )
