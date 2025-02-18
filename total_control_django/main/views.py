from django.http import HttpResponse
from django.shortcuts import render


# Контроллеры
def index(request):
    return render(request, template_name='main/index.html')


def register(request):
    return HttpResponse('Регистрация')
