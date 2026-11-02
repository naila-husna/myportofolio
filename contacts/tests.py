from urllib.parse import urlencode

from django.test import Client, TestCase
from django.urls import reverse

from .models import Contact


class ContactTests(TestCase):
    def setUp(self):
        self.contact = Contact.objects.create(
            name="Ani", email="ani@example.com", phone="081234567890"
        )
        self.data = {"name": "Budi", "email": "budi@example.com", "phone": "+62 812 3456"}

    def test_list_shows_contacts_and_phone(self):
        response = self.client.get(reverse("contacts:contact_list"))
        self.assertContains(response, self.contact.phone)
        self.assertContains(response, 'hx-swap="beforeend"')
        self.assertTemplateUsed(response, "contacts/index.html")

    def test_add_returns_only_new_contact_and_feedback(self):
        response = self.client.post(reverse("contacts:contact_add"), self.data)
        contact = Contact.objects.get(name="Budi")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(contact.phone, self.data["phone"])
        self.assertContains(response, f'id="contact-{contact.pk}"', status_code=201)
        self.assertNotContains(response, f'id="contact-{self.contact.pk}"', status_code=201)
        self.assertContains(response, "Kontak berhasil ditambahkan!", status_code=201)
        self.assertContains(response, 'hx-swap-oob="true"', status_code=201)

    def test_invalid_add_does_not_save(self):
        for invalid in ({"email": "invalid"}, {"name": " "}, {"phone": ""}, {"name": "a" * 101}):
            with self.subTest(invalid=invalid):
                response = self.client.post(reverse("contacts:contact_add"), self.data | invalid)
                self.assertEqual(response.status_code, 422)
        self.assertEqual(Contact.objects.count(), 1)

    def test_search_filters_names_without_case_sensitivity(self):
        Contact.objects.create(**self.data)
        response = self.client.get(reverse("contacts:contact_search"), {"q": "aNI"})
        self.assertContains(response, "ani@example.com")
        self.assertNotContains(response, "budi@example.com")
        response = self.client.get(reverse("contacts:contact_search"), {"q": "missing"})
        self.assertNotContains(response, "<tr")
        response = self.client.get(reverse("contacts:contact_search"), {"q": ""})
        self.assertContains(response, "ani@example.com")
        self.assertContains(response, "budi@example.com")

    def test_add_respects_active_search(self):
        response = self.client.post(reverse("contacts:contact_add"), self.data | {"q": "Ani"})
        self.assertEqual(Contact.objects.count(), 2)
        self.assertNotContains(response, "<tr", status_code=201)
        self.assertContains(response, "Kontak berhasil ditambahkan!", status_code=201)

    def test_edit_and_cancel_leave_contact_unchanged(self):
        response = self.client.get(reverse("contacts:contact_edit", args=[self.contact.pk]))
        self.assertContains(response, f'form="edit-form-{self.contact.pk}"', count=3)
        self.assertContains(response, self.contact.phone)
        response = self.client.get(reverse("contacts:contact_row", args=[self.contact.pk]))
        self.assertNotContains(response, "<input")
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.name, "Ani")

    def test_update_saves_all_fields(self):
        response = self.client.put(
            reverse("contacts:contact_update", args=[self.contact.pk]),
            urlencode(self.data), content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 200)
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.name, "Budi")
        self.assertEqual(self.contact.email, "budi@example.com")
        self.assertEqual(self.contact.phone, "+62 812 3456")
        self.assertNotContains(response, "<input")

    def test_invalid_update_preserves_saved_data(self):
        response = self.client.put(
            reverse("contacts:contact_update", args=[self.contact.pk]),
            urlencode(self.data | {"email": "invalid"}),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 422)
        self.assertContains(response, 'value="invalid"', status_code=422)
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.name, "Ani")
        self.assertEqual(self.contact.email, "ani@example.com")

    def test_update_removes_row_that_no_longer_matches_search(self):
        response = self.client.put(
            reverse("contacts:contact_update", args=[self.contact.pk]),
            urlencode(self.data | {"q": "Ani"}),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.content, b"")
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.name, "Budi")

    def test_delete_returns_empty_200(self):
        response = self.client.delete(reverse("contacts:contact_delete", args=[self.contact.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")
        self.assertFalse(Contact.objects.exists())

    def test_wrong_methods_and_missing_contacts(self):
        for action in ("contact_add", "contact_update", "contact_delete"):
            args = [] if action == "contact_add" else [self.contact.pk]
            response = self.client.get(reverse(f"contacts:{action}", args=args))
            self.assertEqual(response.status_code, 405)
        for action in ("contact_edit", "contact_row"):
            response = self.client.get(reverse(f"contacts:{action}", args=[999999]))
            self.assertEqual(response.status_code, 404)
        self.assertEqual(Contact.objects.count(), 1)

    def test_contact_values_are_html_escaped(self):
        self.contact.name = '<script>alert("test")</script>'
        self.contact.save()
        response = self.client.get(reverse("contacts:contact_row", args=[self.contact.pk]))
        self.assertNotContains(response, "<script>")
        self.assertContains(response, "&lt;script&gt;")

    def test_csrf_is_required_for_mutations(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse("contacts:contact_add"), self.data)
        self.assertEqual(response.status_code, 403)
        client.get(reverse("contacts:contact_list"))
        token = client.cookies["csrftoken"].value
        response = client.post(reverse("contacts:contact_add"), self.data, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 201)
        url = reverse("contacts:contact_update", args=[self.contact.pk])
        payload = urlencode(self.data)
        self.assertEqual(client.put(url, payload, content_type="application/x-www-form-urlencoded").status_code, 403)
        response = client.put(url, payload, content_type="application/x-www-form-urlencoded", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        url = reverse("contacts:contact_delete", args=[self.contact.pk])
        self.assertEqual(client.delete(url).status_code, 403)
        self.assertEqual(client.delete(url, HTTP_X_CSRFTOKEN=token).status_code, 200)
