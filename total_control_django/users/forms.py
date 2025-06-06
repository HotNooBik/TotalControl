from datetime import date

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import MaxValueValidator
from django.contrib.auth import get_user_model


from .models import UserProfile


class UserRegisterForm(UserCreationForm):
    """Форма для регистрации пользователя"""

    error_messages = {
        "password_mismatch": "Пароли не совпадают!",
    }

    username = forms.CharField(
        label="Имя пользователя",
        max_length=50,
        help_text="Обязательное поле. Не более 50 символов. Только буквы, цифры и символы @/./+/-/_.",
        error_messages={
            "required": "Пожалуйста, введите имя пользователя.",
            "max_length": "Имя пользователя не должно превышать 150 символов.",
            "unique": "Пользователь с таким именем уже существует.",
        },
        required=True,
    )

    email = forms.EmailField(
        label="Ваша почта",
        error_messages={
            "required": "Пожалуйста, введите почту.",
            "invalid": "Введите существующую почту.",
        },
        required=True,
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        email_used = get_user_model().objects.filter(email=email).exists()
        if email and email_used:
            raise forms.ValidationError(
                "Пользователь с такой почтой уже существует.",
                code="invalid_email",
            )
        return email

    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput,
        help_text="Пароль должен содержать не менее 8 символов.",
        error_messages={
            "required": "Пожалуйста, введите пароль.",
        },
        required=True,
    )

    password2 = forms.CharField(
        label="Подтверждение пароля",
        strip=False,
        widget=forms.PasswordInput,
        help_text="Введите пароль еще раз для подтверждения.",
        error_messages={
            "required": "Пожалуйста, подтвердите пароль.",
            "password_mismatch": "Пароли не совпадают.",
        },
        required=True,
    )

    birth_date = forms.DateField(
        label="Дата рождения",
        required=True,
        widget=forms.DateInput(attrs={"type": "date"}),
        validators=[
            MaxValueValidator(
                limit_value=date.today(),
                message="Дата рождения не может быть в будущем.",
            )
        ],
        error_messages={
            "required": "Пожалуйста, введите дату рождения.",
        },
    )

    sex = forms.ChoiceField(
        label="Пол",
        choices=UserProfile.sex.field.choices,
        required=True,
        error_messages={
            "required": "Пожалуйста, укажите ваш пол.",
        },
    )

    height = forms.FloatField(
        label="Рост (в см.)",
        required=True,
        min_value=50,
        max_value=300,
        error_messages={
            "required": "Пожалуйста, введите ваш рост.",
            "max_value": "Пожалуйста, введите ваш настоящий рост.",
            "min_value": "Пожалуйста, введите ваш настоящий рост.",
        },
    )

    weight = forms.FloatField(
        label="Вес (в кг.)",
        required=True,
        min_value=5,
        max_value=635,
        error_messages={
            "required": "Пожалуйста, введите ваш вес.",
            "max_value": "Пожалуйста, введите ваш настоящий вес.",
            "min_value": "Пожалуйста, введите ваш настоящий вес.",
        },
    )

    goal = forms.ChoiceField(
        label="Ваша цель",
        choices=UserProfile.goal.field.choices,
        required=True,
        error_messages={
            "required": "Пожалуйста, выберите цель.",
        },
    )

    activity_coef = forms.FloatField(widget=forms.HiddenInput(), initial=1.2)

    def clean_activity_coef(self):
        activity_coef = self.cleaned_data.get("activity_coef")
        return activity_coef if activity_coef in [1.2, 1.375, 1.5, 1.73] else 1.2

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "goal",
            "birth_date",
            "sex",
            "height",
            "weight",
            "activity_coef",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            birth_date = self.cleaned_data.get("birth_date")
            height = round(self.cleaned_data.get("height"), 2)
            weight = round(self.cleaned_data.get("weight"), 2)
            goal = self.cleaned_data.get("goal")
            sex = self.cleaned_data.get("sex")
            activity_coef = self.cleaned_data.get("activity_coef")

            user.save()
            UserProfile.objects.create(
                user=user,
                birth_date=birth_date,
                height=height,
                weight=weight,
                goal=goal,
                sex=sex,
                activity_coef=activity_coef,
            )
        return user


class UserLoginForm(AuthenticationForm):
    """Форма для авторизации пользователя"""

    error_messages = {
        "invalid_login": "Неправильный логин или пароль. Проверьте данные и попробуйте снова.",
        "inactive": "Этот аккаунт неактивен.",
    }
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)


class UserProfileForm(forms.ModelForm):
    """Форма для редактирования данных в профиле"""

    birth_date = forms.DateField(
        label="Дата рождения",
        widget=forms.DateInput(attrs={"type": "date"}),
        validators=[MaxValueValidator(date.today())],
    )

    height = forms.FloatField(
        min_value=50,
        max_value=300,
    )

    weight = forms.FloatField(min_value=5, max_value=635)

    goal = forms.ChoiceField(label="Ваша цель", choices=UserProfile.goal.field.choices)

    sex = forms.ChoiceField(label="Пол", choices=UserProfile.sex.field.choices)

    activity_coef = forms.FloatField(widget=forms.HiddenInput(), initial=1.2)

    def clean_activity_coef(self):
        activity_coef = self.cleaned_data.get("activity_coef")
        return activity_coef if activity_coef in [1.2, 1.375, 1.5, 1.73] else 1.2

    class Meta:
        model = UserProfile
        fields = [
            "goal",
            "birth_date",
            "sex",
            "height",
            "weight",
            "activity_coef",
        ]
