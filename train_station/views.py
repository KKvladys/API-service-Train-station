from django_filters import rest_framework as filters
from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from train_station.filters import (
    StationFilter,
    RouteFilter,
    TripFilter
)
from train_station.models import (
    Station,
    Route,
    TrainType,
    Train,
    Order,
    Trip,
    Crew
)
from train_station.permisions import IsAdminOrIfAuthenticatedReadOnly
from train_station.serializers import (
    CrewSerializer,
    StationSerializer,
    RouteSerializer,
    TrainSerializer,
    OrderSerializer,
    TripSerializer,
    TrainTypeSerializer,
    RouteListSerializer,
    TrainListSerializer,
    OrderListSerializer,
    TripListSerializer,
    CrewListSerializer,
    OrderRetrieveSerializer, TripRetrieveSerializer,
)


class TripOrderViewPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 10


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Crew.objects
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        return CrewSerializer


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = StationFilter
    queryset = Station.objects
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RouteFilter
    queryset = Route.objects.all().select_related("source", "destination")
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        serializer_class = RouteSerializer
        if self.action in ("list", "retrieve"):
            return RouteListSerializer
        return serializer_class


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all().select_related("train_type")
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        serializer_class = TrainSerializer
        if self.action in ("list", "retrieve"):
            return TrainListSerializer
        return serializer_class


class OrderViewSet(viewsets.ModelViewSet):
    pagination_class = TripOrderViewPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Order.objects.prefetch_related(
            "tickets__trip__route__source"
        )
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        serializer_class = OrderSerializer
        if self.action == "list":
            return OrderListSerializer
        if self.action =="retrieve":
            return OrderRetrieveSerializer
        return serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TripViewSet(viewsets.ModelViewSet):
    queryset = (
        Trip.objects.all()
        .select_related(
            "route__source", "route__destination", "train"
        )
        .prefetch_related("crew", "tickets")
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TripFilter
    pagination_class = TripOrderViewPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return TripListSerializer
        if self.action == "retrieve":
            return TripRetrieveSerializer
        return TripSerializer


class TrainTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = TrainType.objects
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminUser,)
