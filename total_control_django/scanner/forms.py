from PIL import Image
from django import forms


class BarcodeUploadForm(forms.Form):
    image = forms.ImageField(
        label="Загрузите изображение со штрих-кодом",
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
                "id": "image-input",
            }
        ),
        required=False,
    )

    def clean_image(self):
        image = self.cleaned_data.get("image")

        if image is None:
            return image

        try:
            img = Image.open(image)
            img.verify()
        except Exception as error:
            raise forms.ValidationError(
                "Файл поврежден или не является изображением."
            ) from error
        return image

    manual_code = forms.CharField(
        label="Введите код вручную",
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "0 7122...",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("image")
        manual_code = cleaned_data.get("manual_code")

        if not image and not manual_code:
            raise forms.ValidationError(
                "Необходимо загрузить изображение или ввести штрих-код вручную."
            )

        return cleaned_data
