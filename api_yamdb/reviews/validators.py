import datetime
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


def validate_year(value):
    current_year = datetime.date.today().year
    if value > current_year:
        raise ValidationError(
            f"Год не может превышать текущий {current_year} год."
        )


username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message=(
        "Допустимыми символами для имени пользователя являются "
        "числа, буквы и символы @/./+/-/_."
    )
)
