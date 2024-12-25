from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField(MinValueValidator(1.0))
    longitude = models.FloatField(MinValueValidator(1.0))

    def __str__(self) -> str:
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Station, related_name="source_routes", on_delete=models.CASCADE
    )
    destination = models.ForeignKey(
        Station, related_name="destination_routes", on_delete=models.CASCADE
    )
    distance = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.source} - {self.destination}"


class TrainType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField(validators=[MinValueValidator(1)])
    places_in_cargo = models.IntegerField(validators=[MinValueValidator(1)])
    train_type = models.ForeignKey(
        TrainType, related_name="trains", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Trip(models.Model):
    route = models.ForeignKey(
        Route, related_name="trips", on_delete=models.CASCADE
    )
    train = models.ForeignKey(
        Train, related_name="trips", on_delete=models.CASCADE
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def clean(self):
        if self.arrival_time <= self.departure_time:
            raise ValidationError("Arrival time must be after departure time.")

    def __str__(self) -> str:
        return f"({str(self.departure_time)}) {str(self.route)} ({str(self.arrival_time)})"

    class Meta:
        unique_together = ("route", "train", "departure_time")


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    trip = models.ForeignKey(
        Trip, related_name="tickets", on_delete=models.CASCADE
    )
    order = models.ForeignKey(
        Order, related_name="tickets", on_delete=models.CASCADE
    )

    @staticmethod
    def validate_ticket(cargo, seat, train, error_to_raise) -> None:
        for ticket_attr_value, ticket_attr_name, train_attr_name in [
            (cargo, "cargo", "cargo_num"),
            (seat, "seat", "places_in_cargo"),
        ]:
            count_attrs = getattr(train, train_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                                          f"number must be in available range: "
                                          f"(1, {train_attr_name}): "
                                          f"(1, {count_attrs})"
                    }
                )

    def clean(self) -> None:
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.trip.train,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"{str(self.trip)} (cargo: {self.cargo}, seat: {self.seat})"

    class Meta:
        unique_together = ("trip", "cargo", "seat")
        ordering = ("cargo", "seat")


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
