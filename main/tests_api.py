from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Message


class MessageAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        cls.visitor = User.objects.create_user(username="visitor", password="test-password")
        cls.editor = User.objects.create_user(username="editor")
        cls.editor.groups.add(Group.objects.create(name="Editor"))
        cls.message = Message.objects.create(
            name="Alya", relationship="Friend", message="Semangat terus!",
        )

    def setUp(self):
        self.list_url = reverse("api:message-list")
        self.detail_url = reverse("api:message-detail", args=[self.message.pk])
        self.star_url = reverse("api:message-star", args=[self.message.pk])
        self.payload = {
            "name": "Budi", "relationship": "Teammate",
            "message": "Terima kasih!", "is_anonymous": False,
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], self.message.pk)
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], self.message.message)
        self.assertNotIn("password", response.data)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"message": "  SEMANGAT  "})
        self.assertEqual([item["id"] for item in response.data], [self.message.pk])
        response = self.client.get(self.list_url, {"message": "not-found"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
        newer = Message.objects.create(**self.payload)
        response = self.client.get(self.list_url, {"message": " "})
        self.assertEqual([item["id"] for item in response.data], [newer.pk, self.message.pk])

    def test_missing_message(self):
        url = reverse("api:message-detail", args=[999999])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.patch(url, {"message": "Changed"}, format="json").status_code, 404)
        self.assertEqual(self.client.delete(url).status_code, 404)
        url = reverse("api:message-star", args=[999999])
        self.assertEqual(self.client.post(url).status_code, 404)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            with self.subTest(user=user):
                self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
                self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 403)
                self.assertEqual(self.client.patch(self.detail_url, {"message": "Changed"}, format="json").status_code, 403)
                self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Message.objects.count(), 1)
        self.message.refresh_from_db()
        self.assertEqual(self.message.message, "Semangat terus!")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        created = Message.objects.get(pk=response.data["id"])
        self.assertEqual(created.message, self.payload["message"])

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for field in ("name", "relationship", "message"):
            for value in ("", "   ", '<img src="x" onerror="alert(1)">'):
                with self.subTest(field=field, value=value):
                    response = self.client.post(self.list_url, self.payload | {field: value}, format="json")
                    self.assertEqual(response.status_code, 400)
                    self.assertIn(field, response.data)
        for field in ("name", "relationship"):
            response = self.client.post(self.list_url, self.payload | {field: "a" * 101}, format="json")
            self.assertEqual(response.status_code, 400)
        self.assertEqual(Message.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"message": "Changed"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.message.refresh_from_db()
        self.assertEqual(self.message.message, "Changed")
        self.assertEqual(self.message.name, "Alya")
        response = self.client.put(self.detail_url, {"message": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.message.refresh_from_db()
        self.assertEqual(self.message.message, "Changed")
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.message.refresh_from_db()
        self.assertEqual(self.message.name, self.payload["name"])
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(Message.objects.filter(pk=self.message.pk).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.client.force_authenticate(user=self.visitor)
        self.message.starred_by.add(self.owner)
        response = self.client.post(self.star_url, {"user": self.owner.pk}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 2)
        self.assertEqual(set(response.data["starred_by_names"].split(", ")), {"owner", "visitor"})
        self.assertTrue(self.client.get(self.detail_url).data["is_starred"])
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertTrue(self.message.starred_by.filter(pk=self.owner.pk).exists())

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload | {
            "id": 999999, "created_at": "2000-01-01T00:00:00Z",
            "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.pk],
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.data["id"], 999999)
        self.assertFalse(response.data["created_at"].startswith("2000-"))
        self.assertEqual(response.data["star_count"], 0)
        self.assertEqual(response.data["starred_by_names"], "")
        self.assertFalse(response.data["is_starred"])

    def test_staff_without_editor_role_cannot_manage_messages(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.client.force_authenticate(user=self.visitor)
        self.assertEqual(self.client.patch(self.detail_url, {"message": "Changed"}, format="json").status_code, 403)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, 405)
        self.assertEqual(self.client.post(self.detail_url, self.payload, format="json").status_code, 405)
        self.assertEqual(self.client.get(self.star_url).status_code, 405)
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get(self.star_url).status_code, 403)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        self.assertEqual(client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(client.patch(self.detail_url, {"message": "Changed"}, format="json").status_code, 403)
        self.assertEqual(client.delete(self.detail_url).status_code, 403)
        self.assertEqual(client.post(self.star_url).status_code, 403)
        self.assertEqual(Message.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, 200)
        token = client.cookies["csrftoken"].value
        headers = {"HTTP_X_CSRFTOKEN": token}
        self.assertEqual(client.post(self.list_url, self.payload, format="json", **headers).status_code, 201)
        self.assertEqual(client.patch(self.detail_url, {"message": "Changed"}, format="json", **headers).status_code, 200)
        self.assertEqual(client.delete(self.detail_url, **headers).status_code, 204)

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self.client.patch(self.detail_url, {"message": "Edited"}, format="json").status_code, 200)
        self.message.refresh_from_db()
        self.assertEqual(self.message.message, "Edited")
        self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 200)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(self.client.post(self.star_url).status_code, 200)
        self.assertEqual(Message.objects.count(), 1)

    def test_anonymous_name_is_hidden_in_all_api_responses(self):
        self.message.is_anonymous = True
        self.message.save()
        for user in (None, self.visitor, self.editor, self.owner):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.get(self.list_url).data[0]["name"], "Anonymous")
            self.assertEqual(self.client.get(self.detail_url).data["name"], "Anonymous")
        self.assertEqual(self.client.post(self.star_url).data["name"], "Anonymous")
        response = self.client.patch(self.detail_url, {"message": "Edited"}, format="json")
        self.assertEqual(response.data["name"], "Anonymous")
        self.message.refresh_from_db()
        self.assertEqual(self.message.name, "Alya")
        response = self.client.post(self.list_url, self.payload | {"is_anonymous": True}, format="json")
        self.assertEqual(response.data["name"], "Anonymous")
        self.assertEqual(Message.objects.get(pk=response.data["id"]).name, "Budi")

    def test_safe_methods_do_not_change_data(self):
        self.message.starred_by.add(self.visitor)
        for url in (self.list_url, self.detail_url):
            for method in ("get", "head", "options"):
                self.assertEqual(getattr(self.client, method)(url).status_code, 200)
        self.assertEqual(Message.objects.count(), 1)
        self.message.refresh_from_db()
        self.assertEqual(self.message.message, "Semangat terus!")
        self.assertEqual(self.message.starred_by.count(), 1)

    def test_text_fields_are_cleaned_and_invalid_patch_does_not_save(self):
        self.client.force_authenticate(user=self.owner)
        payload = {"name": " <b>Alya</b> ", "relationship": " <i>Friend</i> ", "message": " <b>Hello</b> "}
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "Alya")
        self.assertEqual(response.data["relationship"], "Friend")
        self.assertEqual(response.data["message"], "Hello")
        response = self.client.patch(self.detail_url, {"message": "<b></b>"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.message.refresh_from_db()
        self.assertEqual(self.message.message, "Semangat terus!")

    def test_api_login_renders_and_returns_to_list(self):
        url = reverse("rest_framework:login")
        self.assertEqual(url, "/api-auth/login/")
        response = self.client.get(url, {"next": self.list_url})
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        response = self.client.post(url, {
            "username": "owner", "password": "test-password", "next": self.list_url,
        })
        self.assertRedirects(response, self.list_url)

    def test_homepage_uses_api_and_issues_csrf_for_visitor_star(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="visitor", password="test-password"))
        page = client.get(reverse("main:show_main"))
        self.assertContains(page, self.list_url)
        self.assertNotContains(page, "item.fields")
        self.assertNotContains(page, 'id="message-modal"')
        token = client.cookies["csrftoken"].value
        response = client.post(self.star_url, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_starred"])

    def test_invalid_json_is_rejected_without_saving(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, '{"name":', content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Message.objects.count(), 1)
