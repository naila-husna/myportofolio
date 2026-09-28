import json

from django.contrib.auth import get_user_model

from django.test import TestCase
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

    def test_json_uses_username_for_starred_by(self):
        self.message.starred_by.add(self.user)

        response = self.client.get(
            reverse("main:get_messages_json")
        )

        data = json.loads(response.content)

        message_data = next(
            item
            for item in data
            if item["pk"] == self.message.pk
        )

        self.assertEqual(
            message_data["fields"]["starred_by"],
            [["nailahusna"]]
        )