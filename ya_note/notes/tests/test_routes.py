from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()


NOTES_ADD = "notes:add"
NOTES_EDIT = "notes:edit"
NOTES_DELETE = "notes:delete"
USERS_LOGIN = "users:login"


class RoutesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )

    def test_home_page_available_for_any_user(self):
        response = self.client.get(reverse("notes:home"))
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_pages_access(self):
        self.client.login(username="testuser", password="12345")

        response = self.client.get(reverse("notes:list"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("notes:success"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(NOTES_ADD))
        self.assertEqual(response.status_code, 200)

    def test_note_page_access(self):
        self.client.login(username="testuser", password="12345")
        note = Note.objects.create(
            title="Test Note", text="Test Note content", author=self.user
        )

        response = self.client.get(
            reverse("notes:detail", kwargs={"slug": note.slug})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse(NOTES_EDIT, kwargs={"slug": note.slug})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse(NOTES_DELETE, kwargs={"slug": note.slug})
        )
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_user_redirected(self):
        expected_url = reverse(USERS_LOGIN)
        response = self.client.get(reverse("notes:list"))
        self.assertRedirects(
            response, expected_url + "?next=" + reverse("notes:list")
        )

        response = self.client.get(reverse("notes:success"))
        self.assertRedirects(
            response, expected_url + "?next=" + reverse("notes:success")
        )

        response = self.client.get(reverse(NOTES_ADD))
        self.assertRedirects(
            response, expected_url + "?next=" + reverse(NOTES_ADD)
        )

        note = Note.objects.create(
            title="Test Note", text="Test Note content", author=self.user
        )

        response = self.client.get(
            reverse("notes:detail", kwargs={"slug": note.slug})
        )
        self.assertRedirects(
            response,
            expected_url
            + "?next="
            + reverse("notes:detail", kwargs={"slug": note.slug}),
        )

        response = self.client.get(
            reverse(NOTES_EDIT, kwargs={"slug": note.slug})
        )
        self.assertRedirects(
            response,
            expected_url
            + "?next="
            + reverse(NOTES_EDIT, kwargs={"slug": note.slug}),
        )

        response = self.client.get(
            reverse(NOTES_DELETE, kwargs={"slug": note.slug})
        )
        self.assertRedirects(
            response,
            expected_url
            + "?next="
            + reverse(NOTES_DELETE, kwargs={"slug": note.slug}),
        )

    def test_auth_pages_access(self):
        response = self.client.get(reverse("users:signup"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(USERS_LOGIN))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("users:logout"))
        self.assertEqual(response.status_code, 200)
