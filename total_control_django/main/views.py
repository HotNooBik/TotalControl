from django.http import HttpResponse
from django.shortcuts import render


# Контроллеры
def main(request):
    return render(request, template_name='main/base.html')
