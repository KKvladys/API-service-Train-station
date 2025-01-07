from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from train_station.models import (
    Crew,
    Station,
    TrainType,
    Train,
    Route,
    Trip, Ticket, Order
)
from train_station.serializers import (
    StationSerializer,
    TrainTypeSerializer,
    TrainListSerializer,
    TripListSerializer,
    CrewListSerializer,

)
from train_station.tests.base_tests import (
    BaseAuthenticatedTest,
    BaseAdminTest
)

CREW_URL = reverse("train_station:crews-list")
STATION_URL = reverse("train_station:stations-list")
TRAIN_TYPE_URL = reverse("train_station:train-types-list")
TRAIN_URL = reverse("train_station:trains-list")
TRIP_URL = reverse("train_station:trips-list")
ORDER_URL = reverse("train_station:orders-list")


class UnauthenticatedCrewTest(APITestCase):
    def test_auth_requried(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewTest(BaseAuthenticatedTest):
    def setUp(self):
        super().setUp()
        Crew.objects.create(first_name="test_name1", last_name="test_lastname1")
        Crew.objects.create(first_name="test_name2", last_name="test_lastname2")

    def test_crew_list(self):
        res = self.client.get(CREW_URL)
        crews = Crew.objects
        serializer = CrewListSerializer(crews, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_crew_forbidden(self):
        payload = {"first_name": "new_test_name", "last_name": "new_test_lastname"}

        res = self.client.post(CREW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewTest(BaseAdminTest):
    def setUp(self):
        super().setUp()
        Crew.objects.create(first_name="test_name1", last_name="test_lastname1")

    def test_crew_create(self):
        payload = {"first_name": "new_test_name", "last_name": "new_test_lastname"}

        res = self.client.post(CREW_URL, payload)
        crew = Crew.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(crew, key))


class UnauthenticatedStationTest(APITestCase):
    def test_auth_requried(self):
        res = self.client.get(STATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedStationTest(BaseAuthenticatedTest):
    def setUp(self):
        super().setUp()
        Station.objects.create(name="Dnipro1", latitude=10.5, longitude=50.5)
        Station.objects.create(name="Odesa-gol", latitude=8, longitude=60)

    def test_station_list(self):
        res = self.client.get(STATION_URL)
        stations = Station.objects
        serializer = StationSerializer(stations, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_stations_by_name(self):
        res = self.client.get(STATION_URL, {"name": "Dnipro1"})
        stations = Station.objects.filter(name__icontains="Dnipro1")
        serializer = StationSerializer(stations, many=True)
        self.assertEqual(res.data, serializer.data)


class AdminStationTest(BaseAdminTest):
    def setUp(self):
        super().setUp()
        Station.objects.create(name="Dnipro1", latitude=10.5, longitude=50.5)

    def test_station_create_with_valid_latitude_longitude(self):
        payload = {"name": "Lviv", "latitude": 9, "longitude": 40}

        res = self.client.post(STATION_URL, payload)
        station = Station.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(station, key))

    def test_station_create_with_invalid_latitude_longitude(self):
        payload = {"name": "Lviv", "latitude": -200, "longitude": 200}

        res = self.client.post(STATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Latitude must be in range -90 to 90.", res.data["latitude"])
        self.assertIn("Longitude must be in range -180 to 180.", res.data["longitude"])


class UnauthenticatedTrainTypeTest(APITestCase):
    def test_auth_requried(self):
        res = self.client.get(TRAIN_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainTypeTest(BaseAuthenticatedTest):
    def setUp(self):
        super().setUp()

    def test_train_type_list_forbidden(self):
        res = self.client.get(TRAIN_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTrainTypeTest(BaseAdminTest):
    def setUp(self):
        super().setUp()
        TrainType.objects.create(name="Test train type name1")
        TrainType.objects.create(name="Test train type name2")

    def test_train_type_list(self):
        res = self.client.get(TRAIN_TYPE_URL)
        train_types = TrainType.objects
        serializer = TrainTypeSerializer(train_types, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_train_type_create(self):
        payload = {"name": "New train type name"}

        res = self.client.post(TRAIN_TYPE_URL, payload)
        train_type = TrainType.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(train_type, key))


class UnauthenticatedTrainTest(APITestCase):
    def test_auth_requried(self):
        res = self.client.get(TRAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainTest(BaseAuthenticatedTest):
    def setUp(self):
        super().setUp()
        test_train_type = TrainType.objects.create(name="Test train type name")
        self.train = Train.objects.create(
            name="Test name train",
            cargo_num=5,
            places_in_cargo=10,
            train_type=test_train_type,
        )

    def test_correct_view_capacity(self):
        res = self.client.get(TRAIN_URL)

        for train_data in res.data:
            if train_data["name"] == "Test name train":
                expected_capacity = self.train.capacity
                self.assertEqual(train_data["capacity"], expected_capacity)

    def test_trains_list(self):
        res = self.client.get(TRAIN_URL)
        trains = Train.objects
        serializer = TrainListSerializer(trains, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AdminTrainTest(BaseAdminTest):
    def setUp(self):
        super().setUp()

    def test_train_create(self):
        test_train_type = TrainType.objects.create(name="Test train type name")
        payload = {
            "name": "Test train name",
            "cargo_num": 4,
            "places_in_cargo": 40,
            "train_type": test_train_type.id,
        }

        res = self.client.post(TRAIN_URL, payload)
        Train.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class SampleTrips():
    def setUp(self):
        source1 = Station.objects.create(
            name="Test source station1", latitude=10.5, longitude=50.5
        )
        source2 = Station.objects.create(
            name="Test source station2", latitude=4.5, longitude=24.5
        )
        destination1 = Station.objects.create(
            name="Test destination station2", latitude=10.5, longitude=50.5
        )
        destination2 = Station.objects.create(
            name="Test destination station2", latitude=11, longitude=44
        )

        train_type = TrainType.objects.create(name="Test train type")
        train = Train.objects.create(
            name="Test train", cargo_num=3, places_in_cargo=5, train_type=train_type
        )

        crew1 = Crew.objects.create(first_name="Oleg", last_name="Vitov")
        crew2 = Crew.objects.create(first_name="Victor", last_name="Semov")

        route1 = Route.objects.create(
            source=source1, destination=destination1, distance=100
        )
        route2 = Route.objects.create(
            source=source2, destination=destination2, distance=200
        )

        trip1 = Trip.objects.create(
            route=route1,
            train=train,
            departure_time=datetime(2024, 12, 30, 1, 0, 0),
            arrival_time=datetime(2024, 12, 31, 10, 0, 0),
        )
        trip1.crew.add(crew1, crew2)

        trip2 = Trip.objects.create(
            route=route2,
            train=train,
            departure_time=datetime(2025, 1, 5, 0, 0, 0),
            arrival_time=datetime(2025, 1, 6, 10, 0, 0),
        )
        trip2.crew.add(crew1, crew2)


class UnauthenticatedTripTest(APITestCase):
    def test_auth_requried(self):
        res = self.client.get(TRIP_URL)
        res_put = self.client.put(f"{TRIP_URL}1/", {})
        res_delete = self.client.delete(f"{TRIP_URL}1/")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res_put.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res_delete.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTripTest(BaseAuthenticatedTest, SampleTrips):
    def setUp(self):
        super().setUp()
        SampleTrips.setUp(self)

    def test_trip_list(self):
        res = self.client.get(TRIP_URL)
        trips = Trip.objects
        serializer = TripListSerializer(trips, many=True)

        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_trips_by_departure_time(self):
        date = "2024-12-30"
        res = self.client.get(f"{TRIP_URL}?departure_time={date}")

        trips = Trip.objects.filter(departure_time__date=date)
        serializer = TripListSerializer(trips, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(len(res.data["results"]), trips.count())

    def test_filter_trips_by_arrival_time(self):
        date = "2025-1-6"
        res = self.client.get(f"{TRIP_URL}?arrival_time={date}")

        trips = Trip.objects.filter(arrival_time__date=date)
        serializer = TripListSerializer(trips, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(len(res.data["results"]), trips.count())

    def test_trip_tickets_available(self):
        trip = Trip.objects.first()
        train = trip.train
        order = Order.objects.create(user=self.user)
        train.save()

        Ticket.objects.create(trip=trip, cargo=1, seat=1, order=order)
        Ticket.objects.create(trip=trip, cargo=1, seat=2, order=order)
        Ticket.objects.create(trip=trip, cargo=1, seat=3, order=order)

        res = self.client.get(f"{TRIP_URL}{trip.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["tickets_available"], 12)


class AdminTripTest(BaseAdminTest, SampleTrips):
    def setUp(self):
        super().setUp()
        SampleTrips.setUp(self)

    def test_create_trip(self):
        route = Route.objects.first()
        train = Train.objects.first()
        crew = Crew.objects.all()

        payload = {
            "route": route.id,
            "train": train.id,
            "departure_time": datetime(2025, 2, 1, 12, 0, 0).isoformat(),
            "arrival_time": datetime(2025, 2, 1, 18, 0, 0).isoformat(),
            "crew": [member.id for member in crew]
        }
        res = self.client.post(TRIP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Trip.objects.count(), 3)

    def test_admin_delete_trip(self):
        trip = Trip.objects.first()
        url = f"{TRIP_URL}{trip.id}/"

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Trip.objects.filter(id=trip.id).exists())

    def test_create_trip_with_invalid_time(self):
        route = Route.objects.first()
        train = Train.objects.first()
        crew = Crew.objects.all()

        payload = {
            "route": route.id,
            "train": train.id,
            "departure_time": datetime(2025, 2, 1, 18, 0, 0).isoformat(),
            "arrival_time": datetime(2025, 2, 1, 12, 0, 0).isoformat(),  # Некорректное время
            "crew": [member.id for member in crew]
        }
        res = self.client.post(TRIP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Arrival time must be after departure time.", str(res.data))

    def test_create_trip_with_duplicate_train_and_time(self):
        trip = Trip.objects.first()
        route = Route.objects.last()
        crew = Crew.objects.all()

        payload = {
            "route": route.id,
            "train": trip.train.id,
            "departure_time": trip.departure_time.isoformat(),
            "arrival_time": datetime(2025, 2, 1, 20, 0, 0).isoformat(),
            "crew": [member.id for member in crew]
        }
        res = self.client.post(TRIP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This train is already taken at this time.", str(res.data))


class UnauthenticatedOrderTest(APITestCase):
    def test_create_order_unauthenticated(self):
        data = {
            "tickets": [
                {"trip": 1, "cargo": 1, "seat": "A1"}
            ]
        }
        res = self.client.post(ORDER_URL, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_order_list_unauthenticated(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderTest(BaseAuthenticatedTest, SampleTrips):
    def setUp(self):
        super().setUp()
        SampleTrips.setUp(self)

    def test_create_order(self):
        data = {
            "tickets": [
                {
                    "trip": 1,
                    "cargo": 1,
                    "seat": 2,
                }
            ]
        }
        res = self.client.post(ORDER_URL, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.first().user, self.user)

    def test_create_order_with_duplicate_ticket(self):
        data = {
            "tickets": [
                {
                    "trip": 1,
                    "cargo": 1,
                    "seat": 4,
                },
                {
                    "trip": 1,
                    "cargo": 1,
                    "seat": 4,
                }
            ]
        }
        res = self.client.post(ORDER_URL, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_order_list(self):
        Order.objects.create(user=self.user)
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

    def test_get_order_detail(self):
        order = Order.objects.create(user=self.user)
        url = reverse("train_station:orders-detail", args=[order.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["user"], self.user.id)

    def test_create_order_with_multiple_tickets(self):
        data = {
            "tickets": [
                {
                    "trip": 1,
                    "cargo": 1,
                    "seat": 1,
                },
                {
                    "trip": 1,
                    "cargo": 1,
                    "seat": 2,
                }
            ]
        }
        response = self.client.post(ORDER_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(len(response.data["tickets"]), 2)


class AdminOrderTest(BaseAdminTest):
    def setUp(self):
        super().setUp()

    def test_admin_can_see_all_orders(self):
        user = get_user_model().objects.create_user(
            email="anotheruser@mail.tt", password="password123"
        )
        order_another_user = Order.objects.create(user=user)

        url = reverse(
            "train_station:orders-detail",
            kwargs={"pk": order_another_user.id}
        )
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["user"], user.id)
