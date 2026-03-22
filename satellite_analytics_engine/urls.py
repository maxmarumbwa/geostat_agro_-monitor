from django.urls import path
from .views import analyze_point, home

urlpatterns = [
    path("analyze/", analyze_point),
    path("", home),  # 👈 this loads your form
]
