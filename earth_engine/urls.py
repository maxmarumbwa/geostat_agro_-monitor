from django.urls import path
from . import views
from django.views.generic import TemplateView  # Add this import

urlpatterns = [
    # Add your URL patterns here
    # path("test/", views.test, name="test"),
    # path("ndvi/", views.ndvi_view, name="ndvi_view"),
    path("rainfall_raster/", views.rainfall_raster, name="rainfall_raster"),
    path(
        "rainfall_start_end/",
        views.rainfall_start_end,
        name="rainfall_start_end",
    ),
    path(
        "rainfall_cum_start_end_select/",
        views.rainfall_cum_start_end_select,
        name="rainfall_cum_start_end_select",
    ),
]
