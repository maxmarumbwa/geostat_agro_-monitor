# clip rainfall raster to zimbabwe
import json
import ee
from django.shortcuts import render
from django.conf import settings
from pathlib import Path


def rainfall_zimbabwe(request):
    """Display CHIRPS rainfall for Zimbabwe - Fast version"""
    try:
        # Simple bounding box for Zimbabwe
        zimbabwe_bounds = ee.Geometry.Rectangle([20, -23.8, 38, -13.7])

        # Get CHIRPS rainfall
        rainfall = (
            ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
            .filterDate("2023-03-20", "2023-03-21")
            .select("precipitation")
            .mean()
        )

        # Simple bounds instead of complex clipping
        rainfall_region = rainfall.clip(zimbabwe_bounds)

        # Visualization
        vis_params = {
            "min": 0,
            "max": 60,
            "palette": ["ffffcc", "a1dab4", "41b6c4", "2c7fb8", "253494"],
        }

        map_id = rainfall_region.getMapId(vis_params)
        tile_url = map_id["tile_fetcher"].url_format

        # Load GeoJSON for boundary display only (not for clipping)
        geojson_path = (
            Path(settings.BASE_DIR) / "static" / "geojson" / "zimadm1.geojson"
        )
        with open(geojson_path, "r") as f:
            geojson_data = json.load(f)

        context = {
            "tile_url": tile_url,
            "date": "March 20, 2024",
            "center_lat": -19,
            "center_lng": 29,
            "geojson_data": json.dumps(geojson_data),
        }

    except Exception as e:
        context = {"error": str(e)}

    # return render(request, "dashboard/index.html", context)
    return render(request, "rainfall_zimbabwe.html", context)


#
##########################################################################
#############               FIXED DATES              ###########
##########################################################################

# # clip rainfall raster to zimbabwe
# import json
# import ee
# from django.shortcuts import render
# from django.conf import settings
# from pathlib import Path


# def rainfall_zimbabwe(request):
#     """Display CHIRPS rainfall for Zimbabwe - Fast version"""
#     try:
#         # Simple bounding box for Zimbabwe
#         zimbabwe_bounds = ee.Geometry.Rectangle([20, -23.8, 38, -13.7])

#         # Get CHIRPS rainfall
#         rainfall = (
#             ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
#             .filterDate("2023-03-20", "2023-03-21")
#             .select("precipitation")
#             .mean()
#         )

#         # Simple bounds instead of complex clipping
#         rainfall_region = rainfall.clip(zimbabwe_bounds)

#         # Visualization
#         vis_params = {
#             "min": 0,
#             "max": 60,
#             "palette": ["ffffcc", "a1dab4", "41b6c4", "2c7fb8", "253494"],
#         }

#         map_id = rainfall_region.getMapId(vis_params)
#         tile_url = map_id["tile_fetcher"].url_format

#         # Load GeoJSON for boundary display only (not for clipping)
#         geojson_path = (
#             Path(settings.BASE_DIR) / "static" / "geojson" / "zimadm1.geojson"
#         )
#         with open(geojson_path, "r") as f:
#             geojson_data = json.load(f)

#         context = {
#             "tile_url": tile_url,
#             "date": "March 20, 2024",
#             "center_lat": -19,
#             "center_lng": 29,
#             "geojson_data": json.dumps(geojson_data),
#         }

#     except Exception as e:
#         context = {"error": str(e)}

#     # return render(request, "dashboard/index.html", context)
#     return render(request, "rainfall_zimbabwe.html", context)

#############               FIXED DATES  END            ###########


#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
def test(request):
    return render(request, "test.html")


from multiprocessing import context

from django.shortcuts import render
import ee
from datetime import datetime


def satellite_view(request):
    """Display a satellite image from Earth Engine"""
    image = (
        ee.ImageCollection("COPERNICUS/S2")
        .filterDate("2025-01-01", "2026-01-31")
        .filterBounds(ee.Geometry.Point([30.0, -1.0]))
        .first()
    )

    try:
        info = image.getInfo()

        # Extract bands
        bands_list = []
        if "bands" in info:
            for band in info["bands"]:
                bands_list.append(band.get("id", "unknown"))

        # Convert timestamp to readable date
        timestamp = info.get("properties", {}).get("GENERATION_TIME")
        if timestamp:
            # Convert milliseconds to datetime
            readable_date = datetime.fromtimestamp(timestamp / 1000).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        else:
            readable_date = "Unknown"

        context = {
            "image_id": info.get("id", "Unknown"),
            "bands": bands_list,
            "date": readable_date,
            "cloud_cover": info.get("properties", {}).get(
                "CLOUDY_PIXEL_PERCENTAGE", "N/A"
            ),
        }
    except Exception as e:
        context = {"error": str(e)}

    return render(request, "satellite.html", context)


#
#
# #
# View to display rainfall raster
def rainfall_raster(request):
    """Display CHIRPS daily rainfall raster for Malawi"""
    try:
        # Use daily CHIRPS with a single date
        rainfall = (
            ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
            .filterDate("2025-12-20", "2025-12-21")
            .select("precipitation")
            .mean()
        )

        # Clip to Malawi
        malawi = ee.Geometry.Polygon(
            [[[32.7, -17.1], [35.9, -17.1], [35.9, -9.4], [32.7, -9.4], [32.7, -17.1]]]
        )
        rainfall_clipped = rainfall.clip(malawi)

        # Visualization
        vis_params = {
            "min": 0,
            "max": 60,
            "palette": ["ffffcc", "a1dab4", "41b6c4", "2c7fb8", "253494"],
        }

        map_id = rainfall_clipped.getMapId(vis_params)
        tile_url = map_id["tile_fetcher"].url_format

        context = {"tile_url": tile_url, "date": "March 20, 2027"}

    except Exception as e:
        context = {"error": str(e)}

    return render(request, "rainfall_raster.html", context)
    # return render(request, "test.html", context)


################################  with date selector ########################################

from datetime import datetime, timedelta


def rainfall_raster(request):
    """Display CHIRPS daily rainfall raster for Malawi"""
    try:
        # Get date from request
        selected_date = request.GET.get("date", "2025-12-20")

        # Convert to EE format
        start_date = datetime.strptime(selected_date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=1)

        # Format for Earth Engine
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        # Load CHIRPS data
        rainfall = (
            ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
            .filterDate(start_str, end_str)
            .select("precipitation")
            .mean()
        )

        # Malawi boundary
        malawi = ee.Geometry.Polygon(
            [[[32.7, -17.1], [35.9, -17.1], [35.9, -9.4], [32.7, -9.4], [32.7, -17.1]]]
        )

        rainfall_clipped = rainfall.clip(malawi)

        vis_params = {
            "min": 0,
            "max": 60,
            "palette": ["ffffcc", "a1dab4", "41b6c4", "2c7fb8", "253494"],
        }

        map_id = rainfall_clipped.getMapId(vis_params)
        tile_url = map_id["tile_fetcher"].url_format

        context = {
            "tile_url": tile_url,
            "date": start_date.strftime("%B %d, %Y"),
            "selected_date": selected_date,
        }

    except Exception as e:
        context = {"error": str(e)}

    return render(request, "rainfall_raster.html", context)


#
#
#
# # NDVI calculation
# def ndvi_view(request):
#     """Calculate NDVI for a specific area"""
#     # Define your area of interest (farm)
#     # Example: Coordinates for a farm in Rwanda (adjust to your location)
#     farm_roi = ee.Geometry.Polygon(
#         [[[30.9, -17.7], [31.1, -17.7], [31.1, -17.9], [30.9, -17.9], [30.9, -17.7]]]
#     )

#     # Get Sentinel-2 image
#     image = (
#         ee.ImageCollection("COPERNICUS/S2")
#         .filterDate("2025-01-01", "2025-03-22")
#         .filterBounds(farm_roi)
#         .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
#         .first()
#     )

#     if not image:
#         context = {"error": "No cloud-free image available for this period"}
#         return render(request, "ndvi.html", context)

#     # Calculate NDVI = (NIR - Red) / (NIR + Red)
#     nir = image.select("B8")  # NIR band
#     red = image.select("B4")  # Red band
#     ndvi = nir.subtract(red).divide(nir.add(red)).rename("NDVI")

#     # Get statistics for the farm area
#     stats = ndvi.reduceRegion(
#         reducer=ee.Reducer.mean().combine(ee.Reducer.stdDev(), "", True),
#         geometry=farm_roi,
#         scale=10,
#         bestEffort=True,
#     )

#     try:
#         stats_dict = stats.getInfo()

#         context = {
#             "ndvi_mean": round(stats_dict.get("NDVI_mean", 0), 3),
#             "ndvi_std": round(stats_dict.get("NDVI_stdDev", 0), 3),
#             "image_date": image.date().format("YYYY-MM-dd").getInfo(),
#             "farm_area": "Example Farm (Rwanda)",
#             "health_status": get_health_status(stats_dict.get("NDVI_mean", 0)),
#         }
#     except Exception as e:
#         context = {"error": str(e)}

#     return render(request, "ndvi.html", context)


# def get_health_status(ndvi_value):
#     """Classify vegetation health based on NDVI"""
#     if ndvi_value > 0.6:
#         return "Excellent 🌟"
#     elif ndvi_value > 0.4:
#         return "Good ✅"
#     elif ndvi_value > 0.2:
#         return "Moderate ⚠️"
#     elif ndvi_value > 0:
#         return "Poor ❌"
#     else:
#         return "No Vegetation/Water 🏝️"
