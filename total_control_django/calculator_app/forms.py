from django import forms


class FoodEntryForm(forms.Form):
    grams = forms.FloatField(
        label="Граммы",
        min_value=1,
        max_value=99999,
        widget=forms.NumberInput(attrs={"class": "form-control", "id": "grams-input"}),
    )


class OwnFoodEntryForm(forms.Form):
    food_name = forms.CharField(
        label="Название продукта",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "name-input",
                "placeholder": "Введите название продукта",
            }
        ),
    )

    calories = forms.FloatField(
        label="Калории на порцию",
        min_value=0,
        max_value=50000,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "id": "calories-input"}
        ),
    )

    proteins = forms.FloatField(
        label="Всего белков",
        min_value=0,
        max_value=50000,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "id": "proteins-input"}
        ),
    )

    fats = forms.FloatField(
        label="Всего жиров",
        min_value=0,
        max_value=50000,
        widget=forms.NumberInput(attrs={"class": "form-control", "id": "fats-input"}),
    )

    carbs = forms.FloatField(
        label="Всего углеводов",
        min_value=0,
        max_value=50000,
        widget=forms.NumberInput(attrs={"class": "form-control", "id": "carbs-input"}),
    )
