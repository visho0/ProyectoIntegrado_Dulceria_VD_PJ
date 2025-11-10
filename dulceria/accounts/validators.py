import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class ComplexPasswordValidator:
    """
    Validador de contraseñas que exige al menos:
    - una letra mayúscula
    - un dígito numérico
    - un carácter especial (no alfanumérico)
    """

    def validate(self, password, user=None):
        if not any(char.isupper() for char in password):
            raise ValidationError(
                _("La contraseña debe incluir al menos una letra mayúscula."),
                code="password_no_upper",
            )
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                _("La contraseña debe incluir al menos un número."),
                code="password_no_number",
            )
        if not re.search(r"[^\w\s]", password):
            raise ValidationError(
                _("La contraseña debe incluir al menos un carácter especial."),
                code="password_no_special",
            )

    def get_help_text(self):
        return _(
            "La contraseña debe incluir al menos una letra mayúscula, un número y un carácter especial."
        )

