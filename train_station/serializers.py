from collections import defaultdict

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers

from train_station.models import (
    Station,
    Route,
    TrainType,
    Train,
    Order,
    Trip,
    Ticket,
    Crew,
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
    """
    Serializer for a list of routes with station names displayed.
    """
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
    capacity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type",
            "capacity",
        )


class TrainListSerializer(TrainSerializer):
    """
    List of trains with train type displayed.
    """
    train_type = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class CrewListSerializer(CrewSerializer):
    """
    Crew list with full name displayed.
    """
    class Meta:
        model = Crew
        fields = ("id", "full_name")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "trip")


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("cargo", "seat")


class TicketListSerializer(TicketSerializer):
    """
    List of tickets with route.
    """
    route = RouteListSerializer(
        source="trip.route", many=False, read_only=True
    )
    departure_time = serializers.CharField(
        source="trip.departure_time", read_only=True
    )
    arrival_time = serializers.CharField(
        source="trip.arrival_time", read_only=True
    )

    class Meta:
        model = Ticket
        fields = (
            "cargo",
            "seat",
            "route",
            "departure_time",
            "arrival_time",
        )


class TicketDetailSerializer(TicketListSerializer):
    """
    List of tickets with route details.
    """
    source = serializers.CharField(
        source="trip.route.source.name"
    )
    destination = serializers.CharField(
        source="trip.route.destination.name"
    )
    train = serializers.CharField(
        source="trip.train.name", read_only=True
    )

    class Meta:
        model = Ticket
        fields = (
            "id",
            "cargo",
            "seat",
            "source",
            "departure_time",
            "destination",
            "arrival_time",
            "train",
        )


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for working with orders.
    """
    tickets = TicketSerializer(
        many=True, read_only=False, allow_empty=False
    )

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        """
        Creating an order with tickets.
        """
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)

            errors = defaultdict(list)
            for idx, ticket_data in enumerate(tickets_data):
                if Ticket.objects.filter(
                    trip=ticket_data["trip"],
                    cargo=ticket_data["cargo"],
                    seat=ticket_data["seat"]
                ).exists():
                    errors[f"tickets[{idx}]"].append(
                        "Ticket with this trip, cargo, and seat already exists."
                    )
                else:
                    Ticket.objects.create(order=order, **ticket_data)

            if errors:
                raise serializers.ValidationError(errors)

            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(
        many=True, read_only=True
    )


class OrderRetrieveSerializer(OrderSerializer):
    tickets = TicketDetailSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = Order
        fields = ("id", "user", "created_at", "tickets")


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "crew",
        )

    def validate(self, attrs):
        """
        Check if the train is already taken at this time
        and that arrival time is after departure time.
        """
        train = attrs.get("train")
        departure_time = attrs.get("departure_time")
        arrival_time = attrs.get("arrival_time")
        instance_id = self.instance.id if self.instance else None

        if arrival_time and departure_time and arrival_time <= departure_time:
            raise serializers.ValidationError(
                {"arrival_time": "Arrival time must be after departure time."}
            )

        try:
            Trip.validate_train_departure_time(train, departure_time, instance_id)
        except ValidationError as e:
            raise serializers.ValidationError({"trip": e.messages})

        return attrs


class TripListSerializer(TripSerializer):
    """
    List of trips with available tickets.
    """
    route = serializers.SerializerMethodField()
    train = serializers.CharField(source="train.name", read_only=True)
    crew = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )
    tickets_available = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Trip
        fields = (
            "id",
            "route",
            "train",
            "tickets_available",
            "departure_time",
            "arrival_time",
            "crew",
        )

    def get_route(self, obj):
        """
        Get the names trip's source and destination points
        """
        return {
            "source": obj.route.source.name,
            "destination": obj.route.destination.name,
        }

    def get_tickets_available(self, obj):
        """
        Calculating available tickets for the trip.
        """
        tickets_taken = obj.tickets.count()
        capacity = obj.train.capacity
        return capacity - tickets_taken


class TripRetrieveSerializer(TripListSerializer):
    route = RouteListSerializer(
        many=False, read_only=True
    )
    taken_places = TicketSeatsSerializer(
        source="tickets", many=True, read_only=True
    )

    class Meta:
        model = Trip
        fields = (
            "id",
            "route",
            "train",
            "tickets_available",
            "departure_time",
            "arrival_time",
            "crew",
            "taken_places"
        )
