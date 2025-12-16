import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class BRCPFValidator(RegexValidator):
    """
    Based on django-localflavor:
    https://github.com/django/django-localflavor/blob/master/localflavor/br/validators.py
    """

    regex = re.compile(r"^(\d{3})\.(\d{3})\.(\d{3})-(\d{2})$")
    message = _("CPF Inválido.")

    @staticmethod
    def calculate_verification_digit(value, _range):
        calculated_digit = (
            sum([i * int(value[idx]) for idx, i in enumerate(_range)]) % 11
        )

        if calculated_digit >= 2:
            return 11 - calculated_digit
        return 0

    def __call__(self, value):
        if not value.isdigit():
            cpf = self.regex.search(value)
            if cpf:
                value = "".join(cpf.groups())
            else:
                raise ValidationError(self.message, code="invalid")

        if len(value) != 11:
            raise ValidationError(self.message, code="max_digits")

        original_verification_digit = value[-2:]

        first_digit = self.calculate_verification_digit(value, range(10, 1, -1))
        value = value[:-2] + str(first_digit) + value[-1]

        second_digit = self.calculate_verification_digit(value, range(11, 1, -1))
        value = value[:-1] + str(second_digit)

        if value[-2:] != original_verification_digit:
            raise ValidationError(self.message, code="invalid")
        if value.count(value[0]) == 11:
            raise ValidationError(self.message, code="invalid")


class OnlyUpperCaseAndNumbersValidator(RegexValidator):
    regex = r"^[A-Z0-9]*$"
    message = "O código do cupom só pode conter números e letras maiúsculas"

    def __call__(self, value: str) -> None:
        if not re.search(self.regex, value):
            raise ValidationError(self.message, code="invalid")


class OnlyAlphabeticValidator(RegexValidator):
    regex = re.compile(
        r"^[A-Za-záàâåãäéëèêíìïîóôòõöüùúûçñÁÀÂÃÄÅÉÈËÊÍÌÏÎÓÔÕÖÒÙÚÛÜýÿÝŸÇÑèìîòûÈÌÎÒÛ ]+$"
    )
    message = "O campo não pode incluir números ou caracteres especiais"

    def __call__(self, value: str) -> None:
        if not self.regex.search(value):
            raise ValidationError(self.message, code="invalid")
