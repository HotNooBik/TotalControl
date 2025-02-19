from django.shortcuts import render


# Контроллеры
def main(request):
    return render(request, template_name='main/welcome.html')
