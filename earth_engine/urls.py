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
        "district_graph_table/",
        views.district_graph_table,
        name="district_graph_table",
    ),
    path("get_rainfall_tile/", views.get_rainfall_tile, name="get_rainfall_tile"),
    path(
        "test/",
        views.test,
        name="test",
    ),
    path(
        "load_rainfall_map/",
        views.load_rainfall_map,
        name="load_rainfall_map",
    ),
    path("map_animation/", views.map_animation, name="map_animation"),
    #
    #
    ################# NDVI endpoints ################
    #
    #
    path("get_ndvi_tile/", views.get_ndvi_tile, name="get_ndvi_tile"),
    path("load_ndvi_map/", views.load_ndvi_map, name="load_ndvi_map"),
    path(
        "load_ndvi_map_with_shp/",
        views.load_ndvi_map_with_shp,
        name="load_ndvi_map_with_shp",
    ),
    path(
        "get_ndvi_anomaly_tile/",
        views.get_ndvi_anomaly_tile,
        name="get_ndvi_anomaly_tile",
    ),
    path(
        "load_ndvi_ano_rain_map/",
        views.load_ndvi_ano_rain_map,
        name="load_ndvi_ano_rain_map",
    ),
    path("get_ndvi_value/", views.get_ndvi_value, name="get_ndvi_value"),
    path("get_ndvi_timeseries/", views.get_ndvi_timeseries, name="get_ndvi_timeseries"),
    path(
        "get_ndvi_anomaly_timeseries/",
        views.get_ndvi_anomaly_timeseries,
        name="get_ndvi_anomaly_timeseries",
    ),
    path(
        "get_min_max_anom_ndvi_per_pix/",
        views.get_min_max_anom_ndvi_per_pix,
        name="get_min_max_anom_ndvi_per_pix",
    ),
    path("get_ndvi_layers/", views.get_ndvi_layers, name="get_ndvi_layers"),
    path(
        "get_ndvi_layers_start_end/",
        views.get_ndvi_layers_start_end,
        name="get_ndvi_layers_start_end",
    ),
    path(
        "load_ndvi_raster_sub_products_min_max_avg_anom/",
        views.load_ndvi_raster_sub_products_min_max_avg_anom,
    ),
    path(
        "get_ndvi_zonal_timeseries/",
        views.get_ndvi_zonal_timeseries,
        name="get_ndvi_zonal_timeseries",
    ),
    path(
        "report_generator/",
        views.report_generator,
        name="report_generator",
    ),
    # path("get_district_vci/", views.get_district_vci, name="get_district_vci"),
    # path(
    #     "get_all_vegetation_tiles/",
    #     views.get_all_vegetation_tiles,
    #     name="get_all_vegetation_tiles",
    # ),
]
