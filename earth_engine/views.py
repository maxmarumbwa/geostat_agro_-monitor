# Display cumm rainfall for a specific btn and date range
import json
import ee
from django.shortcuts import render
from django.conf import settings
from pathlib import Path


def rainfall_start_end(request):
    """Display CHIRPS rainfall for Zimbabwe - Fast version"""
    try:
        # Simple bounding box for Zimbabwe
        zimbabwe_bounds = ee.Geometry.Rectangle([25, -22.5, 33, -15.5])

        # Get CHIRPS rainfall
        rainfall = (
            ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
            .filterDate("2023-01-20", "2023-03-21")
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
            "date": "March 20, 2023",
            "center_lat": -19,
            "center_lng": 29,
            "geojson_data": json.dumps(geojson_data),
        }

    except Exception as e:
        context = {"error": str(e)}

    return render(request, "rainfall_start_end.html", context)


################################################################################################


####################### select 2 dates dates and selector #######################
#
################################################################################################
def rainfall_cum_start_end_select(request):
    """Display CHIRPS rainfall for Zimbabwe using user-selected date range"""
    try:
        # Get user input (default fallback)
        start_date = request.GET.get("start_date", "2023-01-20")
        end_date = request.GET.get("end_date", "2023-03-21")

        # Zimbabwe bounds
        zimbabwe_bounds = ee.Geometry.Rectangle([25, -22.5, 33, -15.5])

        # CHIRPS rainfall (NOW dynamic)
        rainfall = (
            ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
            .filterDate(start_date, end_date)
            .select("precipitation")
            .sum()  # ✅ cumulative rainfall (IMPORTANT change)
        )

        rainfall_region = rainfall.clip(zimbabwe_bounds)

        vis_params = {
            "min": 0,
            "max": 300,  # increase for cumulative rainfall
            "palette": ["ffffcc", "a1dab4", "41b6c4", "2c7fb8", "253494"],
        }

        map_id = rainfall_region.getMapId(vis_params)
        tile_url = map_id["tile_fetcher"].url_format

        # Load GeoJSON
        geojson_path = (
            Path(settings.BASE_DIR) / "static" / "geojson" / "zimadm1.geojson"
        )
        with open(geojson_path, "r") as f:
            geojson_data = json.load(f)

        context = {
            "tile_url": tile_url,
            "start_date": start_date,
            "end_date": end_date,
            "date": f"{start_date} to {end_date}",
            "center_lat": -19,
            "center_lng": 29,
            "bounds_sw_lat": -22.5,
            "bounds_sw_lng": 25,
            "bounds_ne_lat": -15.5,
            "bounds_ne_lng": 33,
            "geojson_data": json.dumps(geojson_data),
        }

    except Exception as e:
        context = {"error": str(e)}

    return render(request, "rainfall_cum_start_end_select.html", context)


################################################################################################

####################### With date restriction greyout dates and selector #######################
#
################################################################################################

from datetime import datetime, timedelta


def rainfall_raster(request):
    try:
        selected_date = request.GET.get("date", "2025-12-20")

        start_date = datetime.strptime(selected_date, "%Y-%m-%d")
        today = datetime.today()

        # ✅ Must be at least 30 days old
        if (today - start_date).days < 30:
            raise ValueError("Selected date must be at least 30 days before today.")

        if start_date > today:
            raise ValueError("Selected date cannot be in the future.")

        end_date = start_date + timedelta(days=1)

        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        rainfall = (
            ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
            .filterDate(start_str, end_str)
            .select("precipitation")
        )

        if rainfall.size().getInfo() == 0:
            raise ValueError("No rainfall data available for selected date.")

        rainfall = rainfall.mean()

        zimbabwe = ee.Geometry.Polygon(
            [
                [
                    [22.0, -24.5],
                    [35.0, -24.5],
                    [35.0, -13.5],
                    [22.0, -13.5],
                    [22.0, -24.5],
                ]
            ]
        )

        rainfall_clipped = rainfall.clip(zimbabwe)

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


##########################################################################
#############               Get pixel info              ###########
##########################################################################

from django.http import JsonResponse
import ee


def get_rainfall_value(request):
    try:
        lat = float(request.GET.get("lat"))
        lon = float(request.GET.get("lon"))
        date = request.GET.get("date")

        start_date = datetime.strptime(date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=1)

        rainfall = (
            ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
            .filterDate("2023-03-20", "2023-03-25")
            .select("precipitation")
            .mean()
        )

        point = ee.Geometry.Point([lon, lat])

        value = rainfall.reduceRegion(
            reducer=ee.Reducer.mean(), geometry=point, scale=5000
        ).get("precipitation")

        rainfall_value = value.getInfo()

        return JsonResponse({"lat": lat, "lon": lon, "rainfall": rainfall_value})

    except Exception as e:
        return JsonResponse({"error": str(e)})


######################################################################################

################## get rainfall value for a specific point and date ##################

######################################################################################

from django.http import JsonResponse
import ee


def get_rainfall_value(request):
    try:
        lat = float(request.GET.get("lat"))
        lon = float(request.GET.get("lon"))
        date = request.GET.get("date")

        start_date = datetime.strptime(date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=1)

        rainfall = (
            ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
            .filterDate(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
            .select("precipitation")
            .mean()
        )

        point = ee.Geometry.Point([lon, lat])

        value = rainfall.reduceRegion(
            reducer=ee.Reducer.mean(), geometry=point, scale=5000
        ).get("precipitation")

        rainfall_value = value.getInfo()

        return JsonResponse({"lat": lat, "lon": lon, "rainfall": rainfall_value})

    except Exception as e:
        return JsonResponse({"error": str(e)})


######################################################################################

################## get rainfall value for a specific point and date RANGES ##################

######################################################################################
from django.http import JsonResponse
from django.shortcuts import render
import ee
from datetime import datetime, timedelta
import traceback


def validate_date(date_string):
    """Validate date is in YYYY-MM-DD format"""
    try:
        if date_string is None:
            print("validate_date received None")
            return False
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except (ValueError, TypeError) as e:
        print(f"validate_date error: {e}, input: {date_string}")
        return False


def rainfall_page(request):
    """Render the rainfall data page"""
    return render(request, "rainfall.html")


def get_rainfall_cumm_value(request):
    try:
        # Get all parameters
        lat = request.GET.get("lat")
        lon = request.GET.get("lon")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        # DEBUG: Print all request info
        print("=" * 50)
        print(f"REQUEST METHOD: {request.method}")
        print(f"REQUEST PATH: {request.path}")
        print(f"FULL URL: {request.build_absolute_uri()}")
        print(f"GET PARAMETERS: {dict(request.GET)}")
        print(f"lat: {lat} (type: {type(lat)})")
        print(f"lon: {lon} (type: {type(lon)})")
        print(f"start_date: {start_date} (type: {type(start_date)})")
        print(f"end_date: {end_date} (type: {type(end_date)})")
        print("=" * 50)

        # Check for None values
        if lat is None:
            return JsonResponse({"error": "lat parameter is missing"}, status=400)
        if lon is None:
            return JsonResponse({"error": "lon parameter is missing"}, status=400)
        if start_date is None:
            return JsonResponse(
                {"error": "start_date parameter is missing"}, status=400
            )
        if end_date is None:
            return JsonResponse({"error": "end_date parameter is missing"}, status=400)

        # Check for empty strings
        if lat == "":
            return JsonResponse({"error": "lat parameter is empty"}, status=400)
        if lon == "":
            return JsonResponse({"error": "lon parameter is empty"}, status=400)
        if start_date == "":
            return JsonResponse({"error": "start_date parameter is empty"}, status=400)
        if end_date == "":
            return JsonResponse({"error": "end_date parameter is empty"}, status=400)

        # Validate date formats
        if not validate_date(start_date):
            return JsonResponse(
                {"error": f"start_date '{start_date}' must be in YYYY-MM-DD format"},
                status=400,
            )

        if not validate_date(end_date):
            return JsonResponse(
                {"error": f"end_date '{end_date}' must be in YYYY-MM-DD format"},
                status=400,
            )

        # Convert lat/lon to float
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError as e:
            return JsonResponse(
                {"error": f"lat and lon must be valid numbers: {e}"}, status=400
            )

        # Validate coordinate ranges
        if not (-90 <= lat <= 90):
            return JsonResponse(
                {"error": "Latitude must be between -90 and 90"}, status=400
            )

        if not (-180 <= lon <= 180):
            return JsonResponse(
                {"error": "Longitude must be between -180 and 180"}, status=400
            )

        # Get cumulative rainfall data
        try:
            print(
                f"Processing Earth Engine request for lat={lat}, lon={lon}, start={start_date}, end={end_date}"
            )

            # Test Earth Engine initialization
            try:
                test = (
                    ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
                    .limit(1)
                    .size()
                    .getInfo()
                )
                print(f"Earth Engine test successful: {test} images available")
            except Exception as e:
                print(f"Earth Engine test failed: {e}")
                return JsonResponse(
                    {"error": f"Earth Engine connection error: {str(e)}"}, status=500
                )

            # Get rainfall data
            collection = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
            print(f"Filtering from {start_date} to {end_date}")

            filtered = collection.filterDate(start_date, end_date)
            size = filtered.size().getInfo()
            print(f"Found {size} images in date range")

            if size == 0:
                return JsonResponse(
                    {
                        "error": f"No rainfall data available for date range {start_date} to {end_date}",
                        "lat": lat,
                        "lon": lon,
                    },
                    status=404,
                )

            rainfall = filtered.select("precipitation").sum()

            point = ee.Geometry.Point([lon, lat])

            value = rainfall.reduceRegion(
                reducer=ee.Reducer.mean(), geometry=point, scale=5000
            ).get("precipitation")

            rainfall_value = value.getInfo()

            print(f"Rainfall value: {rainfall_value}")

            # Handle null values
            if rainfall_value is None:
                return JsonResponse(
                    {
                        "error": "No rainfall data available for this location",
                        "lat": lat,
                        "lon": lon,
                        "start_date": start_date,
                        "end_date": end_date,
                        "rainfall": None,
                    },
                    status=404,
                )

            return JsonResponse(
                {
                    "lat": lat,
                    "lon": lon,
                    "rainfall": rainfall_value,
                    "start_date": start_date,
                    "end_date": end_date,
                    "units": "mm",
                    "num_days": size,
                }
            )

        except Exception as ee_error:
            print(f"Earth Engine processing error: {traceback.format_exc()}")
            return JsonResponse(
                {"error": f"Earth Engine processing error: {str(ee_error)}"}, status=500
            )

    except Exception as e:
        print(f"General error: {traceback.format_exc()}")
        return JsonResponse({"error": str(e)}, status=500)


#
#
#
#
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
##################################################################################################
#
############################  AOI ###################
#
###################################################################################################
#
#
#
################################  with date selector ########################################

# from datetime import datetime, timedelta


# def rainfall_raster(request):
#     """Display CHIRPS daily rainfall raster for Malawi"""
#     try:
#         # Get date from request
#         selected_date = request.GET.get("date", "2025-12-20")

#         # Convert to EE format
#         start_date = datetime.strptime(selected_date, "%Y-%m-%d")
#         end_date = start_date + timedelta(days=1)

#         # Format for Earth Engine
#         start_str = start_date.strftime("%Y-%m-%d")
#         end_str = end_date.strftime("%Y-%m-%d")

#         # Load CHIRPS data
#         rainfall = (
#             ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
#             .filterDate(start_str, end_str)
#             .select("precipitation")
#             .mean()
#         )

#         # Malawi boundary
#         malawi = ee.Geometry.Polygon(
#             [[[32.7, -17.1], [35.9, -17.1], [35.9, -9.4], [32.7, -9.4], [32.7, -17.1]]]
#         )

#         rainfall_clipped = rainfall.clip(malawi)

#         vis_params = {
#             "min": 0,
#             "max": 60,
#             "palette": ["ffffcc", "a1dab4", "41b6c4", "2c7fb8", "253494"],
#         }

#         map_id = rainfall_clipped.getMapId(vis_params)
#         tile_url = map_id["tile_fetcher"].url_format

#         context = {
#             "tile_url": tile_url,
#             "date": start_date.strftime("%B %d, %Y"),
#             "selected_date": selected_date,
#         }

#     except Exception as e:
#         context = {"error": str(e)}

#     return render(request, "rainfall_raster.html", context)


#
#
# #
# # View to display rainfall raster
# def rainfall_raster(request):
#     """Display CHIRPS daily rainfall raster for Malawi"""
#     try:
#         # Use daily CHIRPS with a single date
#         rainfall = (
#             ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
#             .filterDate("2025-12-20", "2025-12-21")
#             .select("precipitation")
#             .mean()
#         )

#         # Clip to Malawi
#         malawi = ee.Geometry.Polygon(
#             [[[32.7, -17.1], [35.9, -17.1], [35.9, -9.4], [32.7, -9.4], [32.7, -17.1]]]
#         )
#         rainfall_clipped = rainfall.clip(malawi)

#         # Visualization
#         vis_params = {
#             "min": 0,
#             "max": 60,
#             "palette": ["ffffcc", "a1dab4", "41b6c4", "2c7fb8", "253494"],
#         }

#         map_id = rainfall_clipped.getMapId(vis_params)
#         tile_url = map_id["tile_fetcher"].url_format

#         context = {"tile_url": tile_url, "date": "March 20, 2027"}

#     except Exception as e:
#         context = {"error": str(e)}

#     return render(request, "rainfall_raster.html", context)
#     # return render(request, "test.html", context)
#
#
#
#

##################################################################################################
#
############################  AOI ###################
#
###################################################################################################
#
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

#
#
# #
# def test(request):
#     return render(request, "test.html")


# from multiprocessing import context

# from django.shortcuts import render
# import ee
# from datetime import datetime


# def satellite_view(request):
#     """Display a satellite image from Earth Engine"""
#     image = (
#         ee.ImageCollection("COPERNICUS/S2")
#         .filterDate("2025-01-01", "2026-01-31")
#         .filterBounds(ee.Geometry.Point([30.0, -1.0]))
#         .first()
#     )

#     try:
#         info = image.getInfo()

#         # Extract bands
#         bands_list = []
#         if "bands" in info:
#             for band in info["bands"]:
#                 bands_list.append(band.get("id", "unknown"))

#         # Convert timestamp to readable date
#         timestamp = info.get("properties", {}).get("GENERATION_TIME")
#         if timestamp:
#             # Convert milliseconds to datetime
#             readable_date = datetime.fromtimestamp(timestamp / 1000).strftime(
#                 "%Y-%m-%d %H:%M:%S"
#             )
#         else:
#             readable_date = "Unknown"

#         context = {
#             "image_id": info.get("id", "Unknown"),
#             "bands": bands_list,
#             "date": readable_date,
#             "cloud_cover": info.get("properties", {}).get(
#                 "CLOUDY_PIXEL_PERCENTAGE", "N/A"
#             ),
#         }
#     except Exception as e:
#         context = {"error": str(e)}

#     return render(request, "satellite.html", context)
