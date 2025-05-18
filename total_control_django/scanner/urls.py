from django.urls import path
from . import views

urlpatterns = [
    path("", views.barcode_image_scanning, name="barcode_scanning"),
    path("add/<str:barcode>/", views.add_barcode_food, name="add_barcode_food"),
]
