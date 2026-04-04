#################################################################################################
#
######################################### Display NDVI   endpoints ####################################
#
################################################################################################
#
#
from django.http import JsonResponse
import ee


def get_ndvi_tile(request):
    try:
        date = request.GET.get("date", "2025-02-01")

        # -----------------------------
        # 1. Zimbabwe boundary
        # -----------------------------
        zimbabwe = (
            ee.FeatureCollection("FAO/GAUL/2015/level0")
            .filter(ee.Filter.eq("ADM0_NAME", "Zimbabwe"))
            .geometry()
        )

        # -----------------------------
        # 2. MODIS NDVI (native 1km)
        # -----------------------------
        image = (
            ee.ImageCollection("MODIS/061/MOD13A2")
            .filterDate(date, ee.Date(date).advance(16, "day"))
            .select("NDVI")
            .mean()
        )

        # -----------------------------
        # 3. Apply scale factor
        # -----------------------------
        image = image.multiply(0.0001)

        # -----------------------------
        # 4. Clip to Zimbabwe
        # -----------------------------
        # image = image.clip(zimbabwe)

        # -----------------------------
        # 5. Visualization
        # -----------------------------
        vis_params = {"min": 0, "max": 1, "palette": ["brown", "yellow", "green"]}

        map_id = image.getMapId(vis_params)

        return JsonResponse({"tile_url": map_id["tile_fetcher"].url_format})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#############################################################################################
############################  NDVI anomaly map #######################
################################################################################################
#

from django.http import JsonResponse
import ee


def get_ndvi_anomaly_tile(request):
    try:
        date = request.GET.get("date", "2024-01-01")

        # -----------------------------
        # 1. Zimbabwe boundary
        # -----------------------------
        zimbabwe = (
            ee.FeatureCollection("FAO/GAUL/2015/level0")
            .filter(ee.Filter.eq("ADM0_NAME", "Zimbabwe"))
            .geometry()
        )

        target_date = ee.Date(date)

        # -----------------------------
        # 2. CURRENT NDVI
        # -----------------------------
        current = (
            ee.ImageCollection("MODIS/061/MOD13A2")
            .filterDate(target_date, target_date.advance(16, "day"))
            .select("NDVI")
            .mean()
            .multiply(0.0001)
        )

        # -----------------------------
        # 3. BASELINE NDVI (multi-year)
        # Example: 2001–2023 same period
        # -----------------------------
        baseline = (
            ee.ImageCollection("MODIS/061/MOD13A2")
            .filter(ee.Filter.calendarRange(2001, 2023, "year"))
            .filter(
                ee.Filter.dayOfYear(
                    target_date.getRelative("day", "year"),
                    target_date.getRelative("day", "year").add(16),
                )
            )
            .select("NDVI")
            .mean()
            .multiply(0.0001)
        )

        # -----------------------------
        # 4. ANOMALY
        # -----------------------------
        anomaly = current.subtract(baseline)

        # -----------------------------
        # 5. Clip to Zimbabwe
        # -----------------------------
        anomaly = anomaly.clip(zimbabwe)

        # -----------------------------
        # 6. Visualization
        # -----------------------------
        vis_params = {
            "min": -0.5,
            "max": 0.5,
            "palette": [
                "brown",  # negative anomaly (stress)
                "yellow",
                "green",  # positive anomaly
            ],
        }

        map_id = anomaly.getMapId(vis_params)

        return JsonResponse({"tile_url": map_id["tile_fetcher"].url_format})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


##########################################################
############# get ndvi at clicke point
#############################################################

from django.http import JsonResponse
import ee


def get_ndvi_value(request):
    try:
        lat = float(request.GET.get("lat"))
        lon = float(request.GET.get("lon"))
        date = request.GET.get("date", "2024-01-01")

        point = ee.Geometry.Point([lon, lat])

        # NDVI image (same as before)
        image = (
            ee.ImageCollection("MODIS/061/MOD13A2")
            .filterDate(date, ee.Date(date).advance(16, "day"))
            .select("NDVI")
            .mean()
            .multiply(0.0001)
        )

        # Extract value
        value = image.reduceRegion(
            reducer=ee.Reducer.mean(), geometry=point, scale=1000
        ).get("NDVI")

        return JsonResponse({"ndvi": value.getInfo()})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


################################################################
########### NDVI time series at point#############################
####################################################################

from django.http import JsonResponse
import ee
from datetime import datetime, timedelta


def get_ndvi_timeseries(request):
    try:
        lat = float(request.GET.get("lat"))
        lon = float(request.GET.get("lon"))
        start_date = request.GET.get("start_date", "2024-01-01")
        end_date = request.GET.get("end_date", "2024-03-01")

        point = ee.Geometry.Point([lon, lat])

        collection = (
            ee.ImageCollection("MODIS/061/MOD13A2")
            .filterDate(start_date, end_date)
            .select("NDVI")
        )

        def extract_value(image):
            value = image.reduceRegion(
                reducer=ee.Reducer.mean(), geometry=point, scale=1000
            ).get("NDVI")

            return ee.Feature(
                None, {"date": image.date().format("YYYY-MM-dd"), "ndvi": value}
            )

        features = collection.map(extract_value).getInfo()

        data = [
            {
                "date": f["properties"]["date"],
                "ndvi": (f["properties"]["ndvi"] or 0) * 0.0001,
            }
            for f in features["features"]
        ]

        return JsonResponse({"data": data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#
#
#
########################### ndvi AnOMALY GRAPH  ##########################
from django.http import JsonResponse
import ee


def get_ndvi_anomaly_timeseries(request):
    try:
        lat = float(request.GET.get("lat"))
        lon = float(request.GET.get("lon"))
        start_date = request.GET.get("start_date", "2024-01-01")
        end_date = request.GET.get("end_date", "2024-03-01")

        point = ee.Geometry.Point([lon, lat])

        # ---------------- CURRENT NDVI ----------------
        collection = (
            ee.ImageCollection("MODIS/061/MOD13A2")
            .filterDate(start_date, end_date)
            .select("NDVI")
        )

        # ---------------- HISTORICAL ----------------
        historical = (
            ee.ImageCollection("MODIS/061/MOD13A2")
            .filterDate("2001-01-01", "2023-12-31")
            .select("NDVI")
        )

        # ---------------- FUNCTION ----------------
        def extract_values(image):

            date = image.date()
            doy = date.getRelative("day", "year")

            # ✅ STRICT 16-DAY MATCH (NO SMOOTHING)
            seasonal = historical.filter(ee.Filter.dayOfYear(doy, doy.add(15)))

            # ---------------- CLIMATOLOGY ----------------
            baseline_img = seasonal.mean()
            min_img = seasonal.min()
            max_img = seasonal.max()

            # ---------------- REDUCE ----------------
            ndvi_val = image.reduceRegion(
                reducer=ee.Reducer.mean(), geometry=point, scale=1000, bestEffort=True
            ).get("NDVI")

            baseline_val = baseline_img.reduceRegion(
                reducer=ee.Reducer.mean(), geometry=point, scale=1000, bestEffort=True
            ).get("NDVI")

            min_val = min_img.reduceRegion(
                reducer=ee.Reducer.mean(), geometry=point, scale=1000, bestEffort=True
            ).get("NDVI")

            max_val = max_img.reduceRegion(
                reducer=ee.Reducer.mean(), geometry=point, scale=1000, bestEffort=True
            ).get("NDVI")

            # ---------------- ANOMALY ----------------
            anomaly = ee.Number(ndvi_val).subtract(baseline_val)

            return ee.Feature(
                None,
                {
                    "date": date.format("YYYY-MM-dd"),
                    "ndvi": ndvi_val,
                    "baseline": baseline_val,
                    "min": min_val,
                    "max": max_val,
                    "anomaly": anomaly,
                },
            )

        features = collection.map(extract_values).getInfo()

        # ---------------- FORMAT ----------------
        data = []
        for f in features["features"]:
            p = f["properties"]

            data.append(
                {
                    "date": p["date"],
                    "ndvi": (p["ndvi"] or 0) * 0.0001,
                    "baseline": (p["baseline"] or 0) * 0.0001,
                    "min": (p["min"] or 0) * 0.0001,
                    "max": (p["max"] or 0) * 0.0001,
                    "anomaly": (p["anomaly"] or 0) * 0.0001,
                }
            )

        return JsonResponse({"data": data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    #
    #
    #


########################################################################################
########################### get all ndvi layers and display ############################
########################################################################################
from django.http import JsonResponse
import ee


def get_ndvi_layers(request):
    try:
        date = request.GET.get("date", "2024-01-01")

        # ---------------- IMAGE ----------------
        image = (
            ee.ImageCollection("MODIS/061/MOD13A2")
            .filterDate(date, ee.Date(date).advance(16, "day"))
            .select("NDVI")
            .first()
            .multiply(0.0001)
        )

        # ---------------- HISTORICAL ----------------
        historical = (
            ee.ImageCollection("MODIS/061/MOD13A2")
            .filterDate("2001-01-01", "2023-12-31")
            .select("NDVI")
        )

        date_ee = ee.Date(date)
        doy = date_ee.getRelative("day", "year")

        seasonal = historical.filter(ee.Filter.dayOfYear(doy, doy.add(15)))

        baseline = seasonal.mean().multiply(0.0001)
        ndvi_min = seasonal.min().multiply(0.0001)
        ndvi_max = seasonal.max().multiply(0.0001)

        anomaly = image.subtract(baseline)

        # ---------------- VISUALIZATION ----------------
        ndvi_vis = {"min": 0, "max": 1, "palette": ["white", "green"]}
        anomaly_vis = {"min": -0.3, "max": 0.3, "palette": ["red", "white", "green"]}

        # ---------------- TILE URLs ----------------
        ndvi_tile = image.getMapId(ndvi_vis)["tile_fetcher"].url_format
        baseline_tile = baseline.getMapId(ndvi_vis)["tile_fetcher"].url_format
        min_tile = ndvi_min.getMapId(ndvi_vis)["tile_fetcher"].url_format
        max_tile = ndvi_max.getMapId(ndvi_vis)["tile_fetcher"].url_format
        anomaly_tile = anomaly.getMapId(anomaly_vis)["tile_fetcher"].url_format

        return JsonResponse(
            {
                "ndvi": ndvi_tile,
                "baseline": baseline_tile,
                "min": min_tile,
                "max": max_tile,
                "anomaly": anomaly_tile,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


########################################################################################
########################### get all ndvi layers and display ############################
########################################################################################
#
#
#
#########################################################################################
########################### get all ndvi layers and display ############################
########################################################################################
#
#
#
########################################################################################
########################### get all ndvi layers and display ############################
########################################################################################
#

########################################################################################
########################### get all ndvi layers and display ############################
########################################################################################
#
#


###############################################################################
#
#
#
#

# Display cumm rainfall for a specific btn and date range
import json
from urllib import request
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


def test(request):
    return render(request, "test.html")


################################################################################################

#######################Display rainfall with date restriction greyout dates and selector #######################
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


#
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
            .sum()
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
    # return render(request, "rainfall_time_series_all.html", context)


##########################################################################
#############           Get pixel info single date             ###########
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
        print(
            f"Received parameters: lat={lat}, lon={lon}, start_date={start_date}, end_date={end_date}"
        )
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

        return JsonResponse(
            {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "lat": lat,
                "lon": lon,
                "rainfall": rainfall_value,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)})


##########################################################################
#############           Get pixel info 2 dates             ###########
##########################################################################

from django.http import JsonResponse
import ee


def get_rainfall_value_series(request):
    try:
        lat = float(request.GET.get("lat"))
        lon = float(request.GET.get("lon"))
        selected_start_date = request.GET.get("start_date") or "2023-01-01"
        selected_end_date = request.GET.get("end_date") or "2023-01-04"

        start_date = datetime.strptime(selected_start_date, "%Y-%m-%d")
        end_date = datetime.strptime(selected_end_date, "%Y-%m-%d")

        rainfall = (
            ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
            .filterDate(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
            .select("precipitation")
            .sum()
        )

        point = ee.Geometry.Point([lon, lat])

        value = rainfall.reduceRegion(
            reducer=ee.Reducer.mean(), geometry=point, scale=5000
        ).get("precipitation")

        rainfall_value = value.getInfo()

        return JsonResponse(
            {
                "start_date": start_date,
                "end_date": end_date,
                "lat": lat,
                "lon": lon,
                "rainfall": rainfall_value,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)})


################################################################################################
#############           Get pixel info for multiple dates btwn 2 dates             ###########
#################################################################################################

from django.http import JsonResponse
import ee
from datetime import datetime


def get_rainfall_value_series_all(request):
    try:
        # ---------------------------
        # 1. Get query parameters
        # ---------------------------
        lat = request.GET.get("lat")
        lon = request.GET.get("lon")
        start_date_str = request.GET.get("start_date") or "2023-01-01"
        end_date_str = request.GET.get("end_date") or "2023-01-04"

        # Validate lat/lon
        if lat is None or lon is None:
            return JsonResponse({"error": "Missing lat/lon parameters"}, status=400)

        lat = float(lat)
        lon = float(lon)

        # ---------------------------
        # 2. Parse dates
        # ---------------------------
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            return JsonResponse(
                {"error": "Invalid date format. Use YYYY-MM-DD"}, status=400
            )

        # Ensure start <= end
        if start_date > end_date:
            return JsonResponse(
                {"error": "start_date must be before end_date"}, status=400
            )

        # ---------------------------
        # 3. Limit date range (IMPORTANT)
        # ---------------------------
        max_days = 365  # prevent heavy requests
        if (end_date - start_date).days > max_days:
            return JsonResponse(
                {"error": f"Date range too large. Max allowed is {max_days} days."},
                status=400,
            )

        # ---------------------------
        # 4. Load CHIRPS collection
        # ---------------------------
        collection = (
            ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
            .filterDate(start_date_str, end_date_str)
            .select("precipitation")
        )

        point = ee.Geometry.Point([lon, lat])

        # ---------------------------
        # 5. Extract daily values
        # ---------------------------
        def extract_daily(image):
            date = ee.Date(image.get("system:time_start")).format("YYYY-MM-dd")
            rainfall = image.reduceRegion(
                reducer=ee.Reducer.mean(), geometry=point, scale=5000, bestEffort=True
            ).get("precipitation")

            return ee.Feature(None, {"date": date, "rainfall": rainfall})

        features = collection.map(extract_daily)

        # ---------------------------
        # 6. Convert to Python
        # ---------------------------
        feature_list = features.getInfo().get("features", [])

        data = []
        for f in feature_list:
            props = f.get("properties", {})
            data.append(
                {"date": props.get("date"), "rainfall": props.get("rainfall") or 0}
            )

        # ---------------------------
        # 7. Return response
        # ---------------------------
        return JsonResponse(
            {
                "status": "success",
                "lat": lat,
                "lon": lon,
                "start_date": start_date_str,
                "end_date": end_date_str,
                "count": len(data),
                "data": data,
            }
        )

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


#################################################################################################
#############           Get Polygon zonal stats btwn 2 dates             ###########
#################################################################################################

# from django.http import JsonResponse
import ee
from datetime import datetime
import json
from django.conf import settings
import os

# Make sure EE is initialized somewhere in your project
# ee.Initialize()


def get_rainfall_value_series_district(request):
    """
    Get daily rainfall for a district (polygon) between start_date and end_date.
    Expects:
    ?district=<district_name>&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    """
    try:
        district_name = request.GET.get("district")
        start_date_str = request.GET.get("start_date") or "2023-01-01"
        end_date_str = request.GET.get("end_date") or "2023-01-04"

        if not district_name:
            return JsonResponse(
                {"status": "error", "message": "Missing district parameter"}, status=400
            )

        # ---------------------------
        # Parse dates
        # ---------------------------
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            return JsonResponse(
                {"status": "error", "message": "Invalid date format. Use YYYY-MM-DD"},
                status=400,
            )

        if start_date > end_date:
            return JsonResponse(
                {"status": "error", "message": "start_date must be before end_date"},
                status=400,
            )

        # Limit date range
        max_days = 365
        if (end_date - start_date).days > max_days:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"Date range too large. Max {max_days} days",
                },
                status=400,
            )

        # ---------------------------
        # Load CHIRPS collection
        # ---------------------------
        collection = (
            ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
            .filterDate(start_date_str, end_date_str)
            .select("precipitation")
        )

        # ---------------------------
        # Load district polygons
        # ---------------------------
        geojson_path = os.path.join(settings.BASE_DIR, "static/geojson/zimadm1.geojson")
        with open(geojson_path) as f:
            geojson = json.load(f)

        # Find district polygon by name
        district_feature = None
        for feat in geojson["features"]:
            name = feat["properties"].get("ADM1_EN") or feat["properties"].get("")
            if name and name.lower() == district_name.lower():
                district_feature = feat
                break

        if not district_feature:
            return JsonResponse(
                {"status": "error", "message": f"District '{district_name}' not found"},
                status=404,
            )

        geometry = ee.Geometry(district_feature["geometry"])

        # ---------------------------
        # Extract daily mean rainfall
        # ---------------------------
        def extract_daily(image):
            date = ee.Date(image.get("system:time_start")).format("YYYY-MM-dd")
            rainfall = image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=5000,
                bestEffort=True,
            ).get("precipitation")
            return ee.Feature(None, {"date": date, "rainfall": rainfall})

        features = collection.map(extract_daily)

        # ---------------------------
        # Convert to Python list
        # ---------------------------
        feature_list = features.getInfo().get("features", [])

        data = []
        for f in feature_list:
            props = f.get("properties", {})
            data.append(
                {"date": props.get("date"), "rainfall": props.get("rainfall") or 0}
            )

        return JsonResponse(
            {
                "status": "success",
                "district": district_name,
                "start_date": start_date_str,
                "end_date": end_date_str,
                "count": len(data),
                "data": data,
            }
        )

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


#########################################################################################
#
########################     Add rainfall map     ###################################
#
###########################################################################################
# from django.http import JsonResponse
# import ee


# def get_rainfall_tile(request):
#     try:
#         date = request.GET.get("date", "2024-01-01")

#         image = (
#             ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
#             .filterDate(date, ee.Date(date).advance(1, "day"))
#             .first()
#             .select("precipitation")
#         )

#         vis_params = {
#             "min": 0,
#             "max": 50,
#             "palette": ["white", "blue", "green", "yellow", "red"],
#         }

#         map_id = image.getMapId(vis_params)

#         return JsonResponse({"tile_url": map_id["tile_fetcher"].url_format})

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


#########################################################################################
#
########################     Add rainfall map  Limit to Zimbabwe   ###################################
#
###########################################################################################

from django.http import JsonResponse
import ee


def get_rainfall_tile(request):
    try:
        date = request.GET.get("date", "2024-01-01")

        # -----------------------------
        # 1. Load Zimbabwe boundary
        # -----------------------------
        zimbabwe = (
            ee.FeatureCollection("FAO/GAUL/2015/level0")
            .filter(ee.Filter.eq("ADM0_NAME", "Zimbabwe"))
            .geometry()
        )

        # -----------------------------
        # 2. Get CHIRPS rainfall image
        # -----------------------------
        image = (
            ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
            .filterDate(date, ee.Date(date).advance(1, "day"))
            .first()
            .select("precipitation")
        )

        # -----------------------------
        # 3. Clip to Zimbabwe
        # -----------------------------
        image = image.clip(zimbabwe)

        # -----------------------------
        # 4. Visualization parameters
        # -----------------------------
        vis_params = {
            "min": 0,
            "max": 50,
            "palette": ["white", "blue", "green", "yellow", "red"],
        }

        map_id = image.getMapId(vis_params)

        return JsonResponse({"tile_url": map_id["tile_fetcher"].url_format})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#
#
##################################################################################
#
###################### Filtered rainfall map with threshold #######################
#
####################################################################################


from django.http import JsonResponse
import ee


def get_rainfall_tile(request):
    try:
        date = request.GET.get("date", "2024-01-01")
        threshold = request.GET.get("threshold")

        threshold = float(threshold) if threshold else 0

        # Load CHIRPS
        image = (
            ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
            .filterDate(date, ee.Date(date).advance(1, "day"))
            .first()
            .select("precipitation")
        )

        # 🔥 APPLY FILTER (mask values below threshold)
        filtered = image.updateMask(image.gte(threshold))

        vis_params = {
            "min": threshold,
            "max": 50,
            "palette": ["white", "blue", "green", "yellow", "red"],
        }

        map_id = filtered.getMapId(vis_params)

        return JsonResponse({"tile_url": map_id["tile_fetcher"].url_format})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#


#


#
#
#
#


def test(request):
    return render(request, "test.html")


def district_graph_table(request):
    return render(request, "Click polygon for time series graph and table.html")


def load_rainfall_map(request):
    return render(request, "load_rainfall_map_click_polygon.html")


def map_animation(request):
    return render(request, "map_animation.html")


def load_ndvi_map_with_shp(request):
    return render(request, "load_ndvi_map_with_shp.html")


def load_ndvi_map(request):
    return render(request, "load_ndvi_map.html")


def load_ndvi_ano_rain_map(request):
    return render(request, "load_ndvi_ano_rain_map.html")


def load_ndvi_ano_rain_map(request):
    return render(request, "load_ndvi_ano_rain_map.html")


def get_min_max_anom_ndvi_per_pix(request):
    return render(request, "get_min_max_anom_ndvi_per_pix.html")


def load_ndvi_raster_sub_products_min_max_avg_anom(request):
    return render(request, "load_ndvi_raster_sub_products_min_max_avg_anom.html")
