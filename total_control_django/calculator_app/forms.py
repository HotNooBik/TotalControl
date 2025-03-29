from django import forms

class FoodEntryForm(forms.Form):
    grams = forms.FloatField(
        label='Граммы',
        min_value=1,
        max_value=15000,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'grams-input'})
    )