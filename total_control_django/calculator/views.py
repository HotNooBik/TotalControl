from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def calculator(request):
    return render(request, template_name='calculator/calculator.html')