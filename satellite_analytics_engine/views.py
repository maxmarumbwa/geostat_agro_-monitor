from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import PointSerializer
from .utils import is_point_in_zimbabwe
from .gee import get_ndvi_timeseries, initialize_gee


@api_view(["POST"])
def analyze_point(request):
    serializer = PointSerializer(data=request.data)

    if serializer.is_valid():
        lat = serializer.validated_data["latitude"]
        lon = serializer.validated_data["longitude"]

        # 🔒 Restrict to Zimbabwe
        if not is_point_in_zimbabwe(lat, lon):
            return Response({"error": "Point outside Zimbabwe boundary"}, status=400)

        initialize_gee()

        data = get_ndvi_timeseries(lat, lon)

        return Response({"location": [lat, lon], "ndvi_timeseries": data})

    return Response(serializer.errors, status=400)


# display index page
from django.shortcuts import render


def home(request):
    return render(request, "index.html")
