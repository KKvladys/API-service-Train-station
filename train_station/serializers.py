from rest_framework import serializers

from train_station.models import (
    Station,
    Route,
    TrainType,
    Train,
    Order,
    Trip,
    Ticket,
    Crew
)


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type")


class TrainListSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "trip")


class TicketDetailSerializer(TicketSerializer):
    trip = serializers.SerializerMethodField()
    departure_time = serializers.CharField(source="trip.departure_time", read_only=True)
    arrival_time = serializers.CharField(source="trip.arrival_time", read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "trip", "departure_time", "arrival_time")

    def get_trip(self, obj):
        return str(obj.trip.route)

class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")


class OrderDetailSerializer(OrderSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ("id", "route", "train", "departure_time", "arrival_time")


class TripDetailSerializer(TripSerializer):
    route = serializers.SerializerMethodField()
    train = serializers.CharField(source="train.name", read_only=True)

    def get_route(self, obj):
        return str(obj.route)
