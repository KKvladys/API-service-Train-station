from django.urls import path, include
from rest_framework import routers

from train_station.views import CrewViewSet, StationViewSet, RouteViewSet, TrainViewSet, OrderViewSet, TripViewSet, \
     TrainTypeViewSet

router = routers.DefaultRouter()

router.register("crews", CrewViewSet, basename="crew")
router.register("stations", StationViewSet, basename="station")
router.register("routes", RouteViewSet, basename="route")
router.register("trains", TrainViewSet, basename="train")
router.register("orders", OrderViewSet, basename="order")
router.register("trips", TripViewSet, basename="trip")
router.register("train-types", TrainTypeViewSet, basename="train-type")

urlpatterns = [
    path("", include(router.urls))
]

app_name = "train_station"
