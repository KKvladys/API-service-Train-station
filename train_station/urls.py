from django.urls import path, include
from rest_framework import routers

from train_station.views import CrewViewSet, StationViewSet, RouteViewSet, TrainViewSet, OrderViewSet, TripViewSet, \
    TicketViewSet, TrainTypeViewSet

router = routers.DefaultRouter()

router.register("crews", CrewViewSet)
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("trains", TrainViewSet)
router.register("orders", OrderViewSet)
router.register("trips", TripViewSet)
router.register("tickets", TicketViewSet)
router.register("train-types", TrainTypeViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "train_station"
