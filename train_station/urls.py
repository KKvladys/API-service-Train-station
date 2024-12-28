from django.urls import path, include
from rest_framework import routers

from train_station.views import (
    CrewViewSet,
    StationViewSet,
    RouteViewSet,
    TrainViewSet,
    OrderViewSet,
    TripViewSet,
    TrainTypeViewSet,
)

router = routers.DefaultRouter()

router.register("crews", CrewViewSet, basename="crews")
router.register("stations", StationViewSet, basename="stations")
router.register("routes", RouteViewSet, basename="routes")
router.register("trains", TrainViewSet, basename="trains")
router.register("orders", OrderViewSet, basename="orders")
router.register("trips", TripViewSet, basename="trips")
router.register("train-types", TrainTypeViewSet, basename="train-types")

urlpatterns = [path("", include(router.urls))]

app_name = "train_station"
