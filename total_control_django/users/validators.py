from django.contrib.auth.password_validation import (
    MinimumLengthValidator,
    CommonPasswordValidator,
    NumericPasswordValidator,
)
from django.core.exceptions import ValidationError
from django.utils.translation import ngettext

# https://docs.djangoproject.com/en/2.0/_modules/django/contrib/auth/password_validation/#MinimumLengthValidator


class CustomMinimumLengthValidator(MinimumLengthValidator):

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                ngettext(
                    "Этот пароль слишком короткий.",
                    "Этот пароль слишком короткий.",
                    self.min_length,
                ),
                code="password_too_short",
                params={"min_length": self.min_length},
            )

    def get_help_text(self):
        return ngettext(
            "Твой пароль должен содержать как минимум %(min_length)d символ.",
            "Твой пароль должен содержать как минимум %(min_length)d символов.",
            self.min_length,
        ) % {"min_length": self.min_length}


class CustomCommonPasswordValidator(CommonPasswordValidator):

    def validate(self, password, user=None):
        if password.lower().strip() in self.passwords:
            raise ValidationError(
                ("Этот пароль слишком простой."),
                code="password_too_common",
            )

    def get_help_text(self):
        return "Ваш пароль не может быть слишком простым или популярным."


class CustomNumericPasswordValidator(NumericPasswordValidator):

    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                ("Этот пароль полностью состоит из цифр."),
                code="password_entirely_numeric",
            )

    def get_help_text(self):
        return "Ваш пароль не может полностью состоять из цифр."
