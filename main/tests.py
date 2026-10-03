from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Education, Message

User = get_user_model()

class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

class EducationTest(TestCase):
    def setUp(self):
        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            program="Information System",
            start_year=2025,
            end_year=None,
            activities="Pekan Ristek Open Class DSAI 2025",
        )

    def test_education_url_is_accessible(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")

    def test_education_data_appears_on_page(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, self.education.institution)
        self.assertContains(response, self.education.program)
        self.assertContains(response, "2025")
        self.assertContains(response, "Present")

    def test_empty_education_page(self):
        Education.objects.all().delete()
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(
            response,
            "Belum ada data pendidikan yang ditambahkan."
        )
        
class MessageAuthorizationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="reader")
        self.editor = User.objects.create_user(username="editor")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.owner = User.objects.create_user(username="owner", is_superuser=True)
        self.message = Message.objects.create(
            name="Alya",
            relationship="Friend",
            message="Semangat terus!",
        )
        self.message_data = {
            "name": "Alya",
            "relationship": "Friend",
            "message": "Pesan baru.",
        }
        self.main_url = reverse("main:show_main")
        self.edit_url = reverse("main:update_message", args=[self.message.pk])
        self.delete_url = reverse("main:delete_message", args=[self.message.pk])

    def test_public_page_shell_and_create_form_follow_each_role(self):
        for user, is_editor, can_create in [
            (None, False, False),
            (self.user, False, False),
            (self.editor, True, False),
            (self.owner, False, True),
        ]:
            with self.subTest(user=user):
                self.client.logout()
                if user:
                    self.client.force_login(user)

                response = self.client.get(self.main_url)

                self.assertContains(response, '<div id="grid" class="message-grid hide"></div>', html=True)
                self.assertNotContains(response, self.message.message)
                self.assertEqual(response.context["is_editor"], is_editor)
                self.assertEqual('id="message-form"' in response.text, can_create)
                self.assertEqual('id="message-modal"' in response.text, can_create)

                data_response = self.client.get(reverse("main:get_messages_json"))
                self.assertEqual(data_response.status_code, 200)
                self.assertEqual(data_response.json()[0]["fields"]["message"], self.message.message)

    def test_guest_writes_redirect_to_login_without_changing_data(self):
        for url in [self.main_url, self.edit_url, self.delete_url]:
            with self.subTest(url=url):
                response = self.client.post(url, self.message_data)

                self.assertRedirects(response, f'{reverse("main:login")}?next={url}')
                self.assertEqual(Message.objects.count(), 1)
                self.message.refresh_from_db()
                self.assertEqual(self.message.message, "Semangat terus!")

    def test_regular_user_cannot_create_edit_or_delete(self):
        self.client.force_login(self.user)

        for url in [self.main_url, self.edit_url, self.delete_url]:
            with self.subTest(url=url):
                response = self.client.post(url, self.message_data)

                self.assertEqual(response.status_code, 403)
                self.assertEqual(Message.objects.count(), 1)
                self.message.refresh_from_db()
                self.assertEqual(self.message.message, "Semangat terus!")

        self.assertEqual(self.client.get(self.edit_url).status_code, 403)

    def test_editor_can_edit_but_cannot_create_or_delete(self):
        self.client.force_login(self.editor)
        self.assertEqual(self.client.get(self.edit_url).status_code, 200)

        response = self.client.post(self.edit_url, self.message_data)

        self.assertRedirects(response, self.main_url)
        self.message.refresh_from_db()
        self.assertEqual(self.message.message, "Pesan baru.")

        for url in [self.main_url, self.delete_url]:
            with self.subTest(url=url):
                self.assertEqual(self.client.post(url, self.message_data).status_code, 403)
                self.assertEqual(Message.objects.count(), 1)

    def test_owner_can_create_edit_and_delete(self):
        self.client.force_login(self.owner)

        self.assertRedirects(self.client.post(self.main_url, self.message_data), self.main_url)
        self.assertEqual(Message.objects.count(), 2)
        self.assertRedirects(self.client.post(self.edit_url, self.message_data), self.main_url)
        self.message.refresh_from_db()
        self.assertEqual(self.message.message, "Pesan baru.")
        self.assertRedirects(self.client.post(self.delete_url), self.main_url)
        self.assertFalse(Message.objects.filter(pk=self.message.pk).exists())

    def test_get_does_not_delete_message(self):
        self.client.force_login(self.owner)

        self.assertRedirects(self.client.get(self.delete_url), self.main_url)
        self.assertTrue(Message.objects.filter(pk=self.message.pk).exists())


class MessageStarTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="nailahusna",
            password="Password123!"
        )

        self.message = Message.objects.create(
            name="Alya",
            relationship="Friend",
            message="Semangat terus!",
            is_anonymous=False,
        )

    def test_star_requires_login(self):
        response = self.client.post(
            reverse(
                "main:toggle_star",
                args=[self.message.id]
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        self.assertEqual(
            self.message.starred_by.count(),
            0
        )

    def test_logged_in_user_can_star_message(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "main:toggle_star",
                args=[self.message.id]
            )
        )

        self.assertRedirects(
            response,
            reverse("main:show_main")
        )

        self.assertTrue(
            self.message.starred_by.filter(
                pk=self.user.pk
            ).exists()
        )
        self.assertEqual(self.message.starred_by.count(), 1)
        response = self.client.get(reverse("main:get_messages_json"))
        fields = response.json()[0]["fields"]
        self.assertIs(fields["is_starred"], True)
        self.assertEqual(fields["star_count"], 1)

    def test_logged_in_user_can_unstar_message(self):
        self.message.starred_by.add(self.user)

        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "main:toggle_star",
                args=[self.message.id]
            )
        )

        self.assertRedirects(
            response,
            reverse("main:show_main")
        )

        self.assertFalse(
            self.message.starred_by.filter(
                pk=self.user.pk
            ).exists()
        )
        self.assertEqual(self.message.starred_by.count(), 0)
        response = self.client.get(reverse("main:get_messages_json"))
        fields = response.json()[0]["fields"]
        self.assertIs(fields["is_starred"], False)
        self.assertEqual(fields["star_count"], 0)

    def test_get_does_not_change_stars(self):
        self.client.force_login(self.user)

        for already_starred in [False, True]:
            with self.subTest(already_starred=already_starred):
                if already_starred:
                    self.message.starred_by.add(self.user)

                response = self.client.get(reverse("main:toggle_star", args=[self.message.pk]))

                self.assertRedirects(response, reverse("main:show_main"))
                self.assertEqual(self.message.starred_by.filter(pk=self.user.pk).exists(), already_starred)

    def test_users_can_only_toggle_their_own_star(self):
        other_user = User.objects.create_user(username="visitor")
        self.message.starred_by.add(other_user)
        self.client.force_login(self.user)
        star_url = reverse("main:toggle_star", args=[self.message.pk])

        for expected_count in [2, 1, 2]:
            with self.subTest(expected_count=expected_count):
                self.assertRedirects(self.client.post(star_url), reverse("main:show_main"))
                self.assertEqual(self.message.starred_by.count(), expected_count)
                self.assertTrue(self.message.starred_by.filter(pk=other_user.pk).exists())

    def test_star_requires_valid_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        page = client.get(reverse("main:show_main"))
        self.assertContains(page, 'name="csrfmiddlewaretoken"')
        star_url = reverse("main:toggle_star", args=[self.message.pk])

        self.assertEqual(client.post(star_url).status_code, 403)
        self.assertEqual(self.message.starred_by.count(), 0)

        response = client.post(star_url, {
            "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
        })

        self.assertRedirects(response, reverse("main:show_main"))
        self.assertEqual(self.message.starred_by.count(), 1)

    def test_editor_and_owner_can_toggle_stars(self):
        editor = User.objects.create_user(username="editor")
        editor.groups.add(Group.objects.create(name="Editor"))
        owner = User.objects.create_user(username="owner", is_superuser=True)
        star_url = reverse("main:toggle_star", args=[self.message.pk])

        for user in [editor, owner]:
            with self.subTest(user=user):
                self.client.force_login(user)
                self.assertRedirects(self.client.post(star_url), reverse("main:show_main"))
                self.assertTrue(self.message.starred_by.filter(pk=user.pk).exists())
                self.assertRedirects(self.client.post(star_url), reverse("main:show_main"))
                self.assertFalse(self.message.starred_by.filter(pk=user.pk).exists())

    def test_json_uses_username_for_starred_by(self):
        self.user.email = "naila@example.com"
        self.user.save(update_fields=["email"])
        self.message.starred_by.add(self.user)

        response = self.client.get(
            reverse("main:get_messages_json")
        )

        data = response.json()

        message_data = next(
            item
            for item in data
            if item["pk"] == str(self.message.pk)
        )

        self.assertEqual(
            message_data["fields"]["starred_by_names"],
            "nailahusna"
        )
        self.assertEqual(message_data["fields"]["name"], self.message.name)
        self.assertNotContains(response, self.user.email)
        self.assertNotContains(response, self.user.password)

    def test_anonymous_name_is_hidden_for_guests_and_logged_in_users(self):
        self.message.is_anonymous = True
        self.message.save(update_fields=["is_anonymous"])

        for user in [None, self.user]:
            with self.subTest(user=user):
                self.client.logout()
                if user:
                    self.client.force_login(user)

                response = self.client.get(reverse("main:show_main"))

                self.assertNotContains(response, self.message.name)

                data_response = self.client.get(reverse("main:get_messages_json"))
                self.assertEqual(data_response.json()[0]["fields"]["name"], "Anonymous")
                self.assertNotContains(data_response, self.message.name)

    def test_anonymous_name_is_hidden_in_json_without_changing_database(self):
        self.message.is_anonymous = True
        self.message.save(update_fields=["is_anonymous"])

        response = self.client.get(reverse("main:get_messages_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        message_data = next(item for item in response.json() if item["pk"] == str(self.message.pk))
        self.assertEqual(message_data["fields"]["name"], "Anonymous")
        self.assertNotContains(response, self.message.name)
        self.message.refresh_from_db()
        self.assertEqual(self.message.name, "Alya")


class MessageAjaxTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", is_superuser=True)
        self.user = User.objects.create_user(username="reader")
        self.editor = User.objects.create_user(username="editor")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.list_url = reverse("main:get_messages_json")
        self.create_url = reverse("main:create_message_ajax")
        self.message_data = {
            "name": "Alya",
            "relationship": "Friend",
            "message": "Semangat terus!",
        }
        self.message = Message.objects.create(**self.message_data)

    def test_json_includes_message_fields_and_current_users_star_status(self):
        self.message.starred_by.add(self.user)

        for user, is_starred in [(None, False), (self.user, True), (self.editor, False)]:
            with self.subTest(user=user):
                self.client.logout()
                if user:
                    self.client.force_login(user)

                response = self.client.get(self.list_url)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["Content-Type"], "application/json")
                self.assertEqual(response.json(), [{
                    "pk": str(self.message.pk),
                    "fields": {
                        **self.message_data,
                        "is_anonymous": False,
                        "star_count": 1,
                        "is_starred": is_starred,
                        "starred_by_names": self.user.username,
                    },
                }])

    def test_search_matches_message_case_insensitively_and_trims_spaces(self):
        Message.objects.create(name="Semangat", relationship="Friend", message="Terima kasih.")

        response = self.client.get(self.list_url, {"message": "  SEMANGAT  "})

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["pk"] for item in response.json()], [str(self.message.pk)])

    def test_blank_search_returns_all_messages_newest_first(self):
        Message.objects.filter(pk=self.message.pk).update(
            created_at=timezone.now() - timezone.timedelta(days=1)
        )
        newer_message = Message.objects.create(
            name="Budi", relationship="Teammate", message="Terima kasih."
        )

        for params in [{}, {"message": "   "}]:
            with self.subTest(params=params):
                response = self.client.get(self.list_url, params)
                self.assertEqual(
                    [item["pk"] for item in response.json()],
                    [str(newer_message.pk), str(self.message.pk)],
                )

    def test_no_search_matches_and_empty_database_return_empty_list(self):
        response = self.client.get(self.list_url, {"message": "tidak ditemukan"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

        Message.objects.all().delete()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_only_owner_can_create_messages_via_ajax(self):
        for user in [None, self.user, self.editor]:
            with self.subTest(user=user):
                self.client.logout()
                if user:
                    self.client.force_login(user)

                response = self.client.post(self.create_url, self.message_data)

                self.assertEqual(response.status_code, 403)
                self.assertEqual(response["Content-Type"], "application/json")
                self.assertTrue(response.json()["message"])
                self.assertEqual(Message.objects.count(), 1)

    def test_owner_can_create_anonymous_message_and_read_it_via_ajax(self):
        self.client.force_login(self.owner)
        response = self.client.post(self.create_url, {
            **self.message_data, "is_anonymous": "on",
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertTrue(response.json()["message"])
        self.assertEqual(Message.objects.count(), 2)
        created = Message.objects.get(pk=response.json()["pk"])
        self.assertEqual(created.name, self.message_data["name"])
        self.assertEqual(created.relationship, self.message_data["relationship"])
        self.assertEqual(created.message, self.message_data["message"])
        self.assertTrue(created.is_anonymous)

        self.client.logout()
        data = self.client.get(self.list_url).json()
        item = next(item for item in data if item["pk"] == str(created.pk))
        self.assertEqual(item["fields"]["name"], "Anonymous")
        self.assertTrue(item["fields"]["is_anonymous"])
        self.assertEqual(item["fields"]["message"], created.message)
        self.assertEqual(item["fields"]["star_count"], 0)
        self.assertIs(item["fields"]["is_starred"], False)

    def test_create_requires_post(self):
        self.client.force_login(self.owner)

        for method in ["get", "put", "patch", "delete"]:
            with self.subTest(method=method):
                response = getattr(self.client, method)(self.create_url)
                self.assertEqual(response.status_code, 405)
                self.assertEqual(Message.objects.count(), 1)

    def test_invalid_fields_return_json_errors_without_saving(self):
        self.client.force_login(self.owner)

        for field, value, error_code in [
            ("name", "", "required"),
            ("relationship", "", "required"),
            ("message", "   ", "required"),
            ("name", "a" * 101, "max_length"),
            ("relationship", "a" * 101, "max_length"),
        ]:
            with self.subTest(field=field, error_code=error_code):
                response = self.client.post(self.create_url, {
                    **self.message_data, field: value,
                })
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response["Content-Type"], "application/json")
                error = response.json()["errors"][field][0]
                self.assertEqual(error["code"], error_code)
                self.assertTrue(error["message"])
                self.assertEqual(Message.objects.count(), 1)

    def test_html_tags_are_removed_from_all_text_fields_before_saving(self):
        self.client.force_login(self.owner)
        response = self.client.post(self.create_url, {
            "name": " <b>Alya</b> ",
            "relationship": " <i>Friend</i> ",
            "message": "<img src=x onerror=alert(1)>Semangat terus!",
        })

        self.assertEqual(response.status_code, 201)
        created = Message.objects.get(pk=response.json()["pk"])
        for field, value in self.message_data.items():
            self.assertEqual(getattr(created, field), value)

    def test_html_only_input_is_rejected_for_each_text_field(self):
        self.client.force_login(self.owner)

        for field in self.message_data:
            with self.subTest(field=field):
                response = self.client.post(self.create_url, {
                    **self.message_data,
                    field: "<img src=\"x\" onerror=\"alert('XSS!')\">",
                })
                self.assertEqual(response.status_code, 400)
                self.assertTrue(response.json()["errors"][field][0]["message"])
                self.assertEqual(Message.objects.count(), 1)

    def test_create_requires_valid_csrf_header(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        client.get(reverse("main:show_main"))
        token = client.cookies["csrftoken"].value

        for headers in [{}, {"HTTP_X_CSRFTOKEN": "invalid"}]:
            with self.subTest(headers=headers):
                response = client.post(self.create_url, self.message_data, **headers)
                self.assertEqual(response.status_code, 403)
                self.assertEqual(Message.objects.count(), 1)

        response = client.post(
            self.create_url, self.message_data, HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Message.objects.count(), 2)
