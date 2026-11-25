from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from main.models import Project


class ProjectTokenAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser(
            username="project-owner", password="test-password",
        )
        cls.visitor = User.objects.create_user(
            username="project-visitor", password="test-password",
        )

    def setUp(self):
        self.projects_url = reverse("api:project-list")
        self.login_url = reverse("api:api_token_auth")
        self.logout_url = reverse("api:api_logout")
        self.payload = {
            "title": "Portfolio", "description": "Personal portfolio",
            "tech_stack": "Flutter, Django", "project_url": "https://example.com",
        }

    def test_public_list_and_owner_token_create_logout(self):
        response = self.client.get(self.projects_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
        response = self.client.post(self.login_url, {
            "username": self.owner.username, "password": "test-password",
        }, format="json")
        self.assertEqual(response.status_code, 200)
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.post(self.projects_url, self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["project_image_url"], "")
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())
        self.assertEqual(self.client.post(self.logout_url).status_code, 204)
        self.assertFalse(Token.objects.filter(key=token).exists())
        self.assertEqual(self.client.post(self.projects_url, self.payload, format="json").status_code, 401)
        self.client.credentials()
        self.assertEqual(len(self.client.get(self.projects_url).data), 1)

    def test_guest_and_non_owner_cannot_create(self):
        self.assertEqual(self.client.post(self.projects_url, self.payload, format="json").status_code, 401)
        token = Token.objects.create(user=self.visitor)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        self.assertEqual(self.client.post(self.projects_url, self.payload, format="json").status_code, 403)

    def test_invalid_credentials_and_project_url(self):
        response = self.client.post(self.login_url, {
            "username": self.owner.username, "password": "wrong",
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.projects_url, {
            **self.payload, "project_url": "invalid-url",
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("project_url", response.data)

    def test_web_cors_preflight(self):
        response = self.client.options(
            self.projects_url, HTTP_ORIGIN="http://localhost:5000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization,content-type",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "*")

    def test_android_emulator_host(self):
        response = self.client.get(self.projects_url, HTTP_HOST="10.0.2.2:8000")
        self.assertEqual(response.status_code, 200)
