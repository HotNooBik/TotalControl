from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    birth_date = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    height = forms.FloatField(required=False)
    weight = forms.FloatField(required=False)
    goal = forms.ChoiceField(choices=UserProfile.goal.field.choices, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "birth_date",
            "height",
            "weight",
            "goal",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                birth_date=self.cleaned_data.get("birth_date"),
                height=self.cleaned_data.get("height"),
                weight=self.cleaned_data.get("weight"),
                goal=self.cleaned_data.get("goal"),
            )
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
