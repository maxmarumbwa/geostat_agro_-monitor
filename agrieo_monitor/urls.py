from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("", include("satellite_analytics_engine.urls")),
    path("", include("earth_engine.urls")),
]
