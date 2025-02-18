from django.http import HttpResponse
from django.shortcuts import render


# Контроллеры
def home(request):
    return render(request, template_name='main/home.html')
