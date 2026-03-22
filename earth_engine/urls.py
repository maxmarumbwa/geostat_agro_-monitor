from django.urls import path
from . import views

urlpatterns = [
    # Add your URL patterns here
    path("satellite/", views.satellite_view, name="satellite_view"),
    path("ndvi/", views.ndvi_view, name="ndvi_view"),
    path("rainfall_raster/", views.rainfall_raster, name="rainfall_raster"),
]
