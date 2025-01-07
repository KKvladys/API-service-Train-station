from django_filters import rest_framework as filters

from train_station.models import Station, Route, Trip


class StationFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Station
        fields = ("name",)


class RouteFilter(filters.FilterSet):
    source = filters.CharFilter(field_name="source__name", lookup_expr="icontains")
    destination = filters.CharFilter(
        field_name="destination__name", lookup_expr="icontains"
    )

    class Meta:
        model = Route
        fields = ("source", "destination")


class TripFilter(filters.FilterSet):
    source_station = filters.CharFilter(
        field_name="route__source__name", lookup_expr="icontains"
    )
    destination_station = filters.CharFilter(
        field_name="route__destination__name", lookup_expr="icontains"
    )
    departure_time = filters.DateFilter(
        field_name="departure_time", lookup_expr="date"
    )
    arrival_time = filters.DateFilter(
        field_name="arrival_time", lookup_expr="date"
    )

    class Meta:
        model = Trip
        fields = ("source_station", "destination_station", "departure_time")
