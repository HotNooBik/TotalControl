from django import forms


class FoodEntryForm(forms.Form):

    unit = forms.ChoiceField(
        label="Единица измерения",
        choices=[],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    amount = forms.FloatField(
        label="Количество",
        min_value=0.1,
        max_value=99999,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "id": "amount-input", "step": "0.1"}
        ),
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
        label="Калорий",
        min_value=0,
        max_value=50000,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "calories-input",
                "placeholder": "...",
            }
        ),
    )

    proteins = forms.FloatField(
        label="Белков",
        min_value=0,
        max_value=50000,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "proteins-input",
                "placeholder": "...",
            }
        ),
    )

    fats = forms.FloatField(
        label="Жиров",
        min_value=0,
        max_value=50000,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "fats-input",
                "placeholder": "...",
            }
        ),
    )

    carbs = forms.FloatField(
        label="Углеводов",
        min_value=0,
        max_value=50000,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "carbs-input",
                "placeholder": "...",
            }
        ),
    )
