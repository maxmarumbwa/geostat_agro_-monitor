from django.urls import path
from . import views
from django.views.generic import TemplateView  # Add this import

urlpatterns = [
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
    path("get_rainfall_value/", views.get_rainfall_value, name="get_rainfall_value"),
    path(
        "get_rainfall_value_series/",
        views.get_rainfall_value_series,
        name="get_rainfall_value_series",
    ),
    path(
        "get_rainfall_value_series/",
        views.get_rainfall_value_series,
        name="get_rainfall_value_series",
    ),
    path(
        "get_rainfall_value_series_all/",
        views.get_rainfall_value_series_all,
        name="get_rainfall_value_series_all",
    ),
    path(
        "get_rainfall_value_series_district/",
        views.get_rainfall_value_series_district,
        name="get_rainfall_value_series_district",
    ),
    path(
        "test/",
        views.test,
        name="test",
    ),
]
