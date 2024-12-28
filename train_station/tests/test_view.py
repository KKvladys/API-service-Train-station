from datetime import datetime

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from train_station.models import (
    Crew,
    Station,
    TrainType,
    Train,
    Route,
    Trip
)
from train_station.serializers import (
    CrewSerializer,
    StationSerializer,
    TrainTypeSerializer,
    TrainListSerializer,
    TripListSerializer,

)
from train_station.tests.base_tests import BaseAuthenticatedTest, BaseAdminTest


CREW_URL = reverse("train_station:crews-list")
STATION_URL = reverse("train_station:stations-list")
TRAIN_TYPE_URL = reverse("train_station:train-types-list")
TRAIN_URL = reverse("train_station:trains-list")
TRIP_URL = reverse("train_station:trips-list")


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
        serializer = CrewSerializer(crews, many=True)
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

    def test_station_create(self):
        payload = {"name": "Lviv", "latitude": 9, "longitude": 40}

        res = self.client.post(STATION_URL, payload)
        station = Station.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(station, key))


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
        Train.objects.create(
            name="Test name train",
            cargo_num=5,
            places_in_cargo=10,
            train_type=test_train_type,
        )

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


class UnauthenticatedTripTest(APITestCase):
    def test_auth_requried(self):
        res = self.client.get(TRIP_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTripTest(BaseAuthenticatedTest):
    def setUp(self):
        super().setUp()

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
            departure_time=datetime(2024, 12, 31, 0, 0, 0),
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

    def test_trip_list(self):
        res = self.client.get(TRIP_URL)
        trips = Trip.objects
        serializer = TripListSerializer(trips, many=True)

        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
