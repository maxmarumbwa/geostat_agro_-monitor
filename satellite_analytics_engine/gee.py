import ee


def initialize_gee():
    try:
        ee.Initialize()
    except:
        ee.Authenticate()
        ee.Initialize()


def get_ndvi_timeseries(lat, lon):
    point = ee.Geometry.Point([lon, lat])

    collection = (
        ee.ImageCollection("MODIS/006/MOD13Q1")
        .select("NDVI")
        .filterDate("2020-01-01", "2022-12-31")
        .filterBounds(point)
    )

    def extract(image):
        value = image.reduceRegion(reducer=ee.Reducer.mean(), geometry=point, scale=250)
        return ee.Feature(
            None, {"date": image.date().format(), "ndvi": value.get("NDVI")}
        )

    results = collection.map(extract).getInfo()

    return results
