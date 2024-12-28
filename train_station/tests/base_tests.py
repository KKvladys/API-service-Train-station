from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class BaseAuthenticatedTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@mail.tt", password="testpassword"
        )
        self.client.force_authenticate(self.user)


class BaseAdminTest(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            email="admin@mail.tt", password="adminpassword"
        )
        self.client.force_authenticate(self.admin)
