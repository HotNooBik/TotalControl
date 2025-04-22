from django import forms
from .models import UserCustomFood


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
                "placeholder": "Введите название продукта...",
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


class UserCustomFoodForm(forms.ModelForm):
    def __init__(self, *args, target="portion", **kwargs):
        self.target = target
        super().__init__(*args, **kwargs)

    food_name = forms.CharField(
        label="Название продукта",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "name-input",
                "placeholder": "Введите название продукта...",
            }
        ),
    )

    brand_name = forms.CharField(
        label="Название бренда продукта (если есть)",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "brand-input",
                "placeholder": "Введите название бренда...",
            }
        ),
    )

    serving_name = forms.CharField(
        label="Название порции",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "serving-input",
                "placeholder": "1 порция...",
            }
        ),
    )

    calories = forms.FloatField(
        label="Калорий на порцию",
        min_value=0,
        max_value=50000,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "calories-input",
                "placeholder": "...",
            }
        ),
    )

    proteins = forms.FloatField(
        label="Белков на порцию",
        min_value=0,
        max_value=50000,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "proteins-input",
                "placeholder": "...",
            }
        ),
    )

    fats = forms.FloatField(
        label="Жиров на порцию",
        min_value=0,
        max_value=50000,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "fats-input",
                "placeholder": "...",
            }
        ),
    )

    carbs = forms.FloatField(
        label="Углеводов на порцию",
        min_value=0,
        max_value=50000,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "carbs-input",
                "placeholder": "...",
            }
        ),
    )

    calories_100g = forms.FloatField(
        label="Калорий на 100 г.",
        min_value=0,
        max_value=50000,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "calories-100g-input",
                "placeholder": "...",
            }
        ),
    )

    proteins_100g = forms.FloatField(
        label="Белков на 100 г.",
        min_value=0,
        max_value=50000,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "proteins-100g-input",
                "placeholder": "...",
            }
        ),
    )

    fats_100g = forms.FloatField(
        label="Жиров на 100 г.",
        min_value=0,
        max_value=50000,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "fats-100g-input",
                "placeholder": "...",
            }
        ),
    )

    carbs_100g = forms.FloatField(
        label="Углеводов на 100 г.",
        min_value=0,
        max_value=50000,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "carbs-100g-input",
                "placeholder": "...",
            }
        ),
    )

    calories_100ml = forms.FloatField(
        label="Калорий на 100 мл.",
        min_value=0,
        max_value=50000,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "calories-100ml-input",
                "placeholder": "...",
            }
        ),
    )

    proteins_100ml = forms.FloatField(
        label="Белков на 100 мл.",
        min_value=0,
        max_value=50000,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "proteins-100ml-input",
                "placeholder": "...",
            }
        ),
    )

    fats_100ml = forms.FloatField(
        label="Жиров на 100 мл.",
        min_value=0,
        max_value=50000,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "fats-100ml-input",
                "placeholder": "...",
            }
        ),
    )

    carbs_100ml = forms.FloatField(
        label="Углеводов на 100 мл.",
        min_value=0,
        max_value=50000,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "carbs-100ml-input",
                "placeholder": "...",
            }
        ),
    )

    class Meta:
        model = UserCustomFood
        fields = [
            "food_name",
            "brand_name",
            "serving_name",
            "calories",
            "proteins",
            "fats",
            "carbs",
            "calories_100g",
            "proteins_100g",
            "fats_100g",
            "carbs_100g",
            "calories_100ml",
            "proteins_100ml",
            "fats_100ml",
            "carbs_100ml",
        ]

    def clean(self):
        prefixes = ["", "_100g", "_100ml"]
        targets = ["portion", "per100g", "per100ml"]
        errors = [
            "Заполните все поля в КБЖУ на порцию.",
            "Заполните все поля в КБЖУ на 100 г.",
            "Заполните все поля в КБЖУ на 100 мл.",
        ]

        all_groups_is_empty = True
        cleaned_data = super().clean()

        for i in (0, 1, 2):
            fields = [
                cleaned_data.get(nutrient + prefixes[i])
                for nutrient in ["calories", "proteins", "fats", "carbs"]
            ]
            is_empty = all(f is None for f in fields)
            has_missed = not is_empty and any(f is None for f in fields)
            if has_missed:
                self.target = targets[i]
                raise forms.ValidationError(errors[i])
            if not is_empty:
                all_groups_is_empty = False

        if all_groups_is_empty:
            raise forms.ValidationError("Заполните КБЖУ хотя бы для одного варианта.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        nutrients = ["calories", "proteins", "fats", "carbs"]

        brand_name = self.cleaned_data.get("brand_name").strip()
        if not brand_name:
            instance.brand_name = None
        else:
            instance.brand_name = brand_name

        serving_name = self.cleaned_data.get("serving_name", "").strip()
        if not serving_name:
            instance.serving_name = "1 порция"
        else:
            instance.serving_name = serving_name

        if not self.cleaned_data.get("calories"):
            if self.cleaned_data.get("calories_100g"):
                instance.serving_name = "100 г."
                for nutrient in nutrients:
                    setattr(
                        instance, nutrient, self.cleaned_data.get(f"{nutrient}_100g")
                    )
            elif self.cleaned_data.get("calories_100ml"):
                instance.serving_name = "100 мл."
                for nutrient in nutrients:
                    setattr(
                        instance, nutrient, self.cleaned_data.get(f"{nutrient}_100ml")
                    )

        if commit:
            instance.save()
        return instance
