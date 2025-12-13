import re
from ..models.exceptions import ValidationError

def validate_nim(nim: str):
    if not re.fullmatch(r'^\d{12}$', nim):
        raise ValidationError("NIM harus berupa 12 digit angka.")