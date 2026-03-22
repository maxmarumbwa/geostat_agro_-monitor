import geopandas as gpd
from shapely.geometry import Point

# Load once at startup
gdf = gpd.read_file("static/geojson/zimadm1.geojson")
ZIM_BOUNDARY = gdf.geometry.union_all()  # ✅ computed once


def is_point_in_zimbabwe(lat, lon):
    point = Point(lon, lat)
    return ZIM_BOUNDARY.contains(point)
