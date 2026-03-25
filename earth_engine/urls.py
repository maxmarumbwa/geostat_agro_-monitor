from django.urls import path
from . import views

urlpatterns = [
    # Add your URL patterns here
    # path("test/", views.test, name="test"),
    # path("ndvi/", views.ndvi_view, name="ndvi_view"),
    path("rainfall_raster/", views.rainfall_raster, name="rainfall_raster"),
    path("rainfall_zimbabwe/", views.rainfall_zimbabwe, name="rainfall_zimbabwe"),
]
