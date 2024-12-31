from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


def validate_latitude(value):
    if not (-90 <= value <= 90):
        raise ValidationError(
            "Latitude must be in range -90 to 90."
        )


def validate_longitude(value):
    if not (-180 <= value <= 180):
        raise ValidationError(
            "Longitude must be in range -180 to 180."
        )


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField(validators=[validate_latitude])
    longitude = models.FloatField(validators=[validate_longitude])

    class Meta:
        verbose_name = "Station"
        verbose_name_plural = "Stations"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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

    class Meta:
        verbose_name = "Route"
        verbose_name_plural = "Routes"
        indexes = [
            models.Index(fields=["source", "destination"]),
        ]

    def clean(self) -> None:
        if self.source == self.destination:
            raise ValidationError(
                "Source and destination cannot be the same."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class TrainType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Train Type"
        verbose_name_plural = "Train Types"

    def __str__(self) -> str:
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField(validators=[MinValueValidator(1)])
    places_in_cargo = models.IntegerField(validators=[MinValueValidator(1)])
    train_type = models.ForeignKey(
        TrainType, related_name="trains", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Train"
        verbose_name_plural = "Trains"
        unique_together = ("name", "train_type")

    @property
    def capacity(self):
        return self.cargo_num * self.places_in_cargo

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
        verbose_name = "Order"
        verbose_name_plural = "Orders"


class Trip(models.Model):
    route = models.ForeignKey(
        Route, related_name="trips", on_delete=models.CASCADE
    )
    train = models.ForeignKey(
        Train, related_name="trips", on_delete=models.CASCADE
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField("Crew", related_name="trips")

    class Meta:
        ordering = ("departure_time",)
        verbose_name = "Trip"
        verbose_name_plural = "Trips"

    @staticmethod
    def validate_train_departure_time(train, departure_time, instance_id=None):
        """
        Validate unique fields train и departure_time.
        """
        query = Trip.objects.filter(
            train=train, departure_time=departure_time
        )
        if instance_id:
            query = query.exclude(id=instance_id)

        if query.exists():
            raise ValidationError(
                "This train is already taken at this time."
            )

    def clean(self):
        if self.arrival_time <= self.departure_time:
            raise ValidationError(
                "Arrival time must be after departure time."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"({str(self.departure_time)}) "
            f"{str(self.route)} "
            f"({str(self.arrival_time)})"
        )


class Ticket(models.Model):
    cargo = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    trip = models.ForeignKey(
        Trip, related_name="tickets", on_delete=models.CASCADE
    )
    order = models.ForeignKey(
        Order, related_name="tickets", on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["trip", "cargo", "seat"],
                name="unique_trip_cargo_seat"
            )
        ]
        ordering = ("cargo", "seat")
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"

    @staticmethod
    def validate_ticket(cargo, seat, train):
        constraints = {
            "cargo": train.cargo_num,
            "seat": train.places_in_cargo,
        }
        for field, max_value in constraints.items():
            value = locals()[field]
            if not (1 <= value <= max_value):
                raise ValidationError(
                    f"{field.capitalize()} must be between 1 and {max_value}."
                )

    def clean(self) -> None:
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.trip.train,
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
            force_insert,
            force_update,
            using,
            update_fields
        )

    def __str__(self):
        return (f"{str(self.trip)} "
                f" (cargo: {self.cargo}, "
                f"seat: {self.seat})")


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    class Meta:
        verbose_name = "Crew"
        verbose_name_plural = "Crews"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
