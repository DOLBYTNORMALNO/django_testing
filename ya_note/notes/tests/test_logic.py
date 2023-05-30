from django.urls import reverse
from pytils.translit import slugify
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()


class LogicTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username="testuser1", password="12345"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", password="12345"
        )

    def test_authenticated_user_can_create_note(self):
        self.client.login(username="testuser1", password="12345")
        note_data = {"title": "Test Note", "text": "Test Note content"}

        response = self.client.post(
            reverse("notes:add"), data=note_data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Note.objects.count(), 1)

    def test_anonymous_user_cannot_create_note(self):
        note_data = {"title": "Test Note", "text": "Test Note content"}

        response = self.client.post(
            reverse("notes:add"), data=note_data, follow=True
        )
        self.assertRedirects(
            response, reverse("users:login") + "?next=" + reverse("notes:add")
        )

    def test_cannot_create_two_notes_with_same_slug(self):
        self.client.login(username="testuser1", password="12345")
        note_data = {
            "title": "Test Note",
            "text": "Test Note content",
            "slug": "test-note",
        }

        response = self.client.post(
            reverse("notes:add"), data=note_data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Note.objects.count(), 1)

        response = self.client.post(
            reverse("notes:add"), data=note_data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Note.objects.count(), 1)

    def test_slug_autogenerated_if_not_provided(self):
        self.client.login(username="testuser1", password="12345")
        note_data = {"title": "Test Note", "text": "Test Note content"}

        response = self.client.post(
            reverse("notes:add"), data=note_data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        note = Note.objects.first()
        self.assertEqual(note.slug, slugify(note_data["title"]))

    def test_user_can_edit_and_delete_own_notes(self):
        self.client.login(username="testuser1", password="12345")
        note = Note.objects.create(
            title="Test Note", text="Test Note content", author=self.user1
        )

        note_data = {"title": "Updated Note", "text": "Updated content"}
        response = self.client.post(
            reverse("notes:edit", kwargs={"slug": note.slug}),
            data=note_data,
            follow=True,
        )
        note.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(note.title, "Updated Note")
        self.assertEqual(note.text, "Updated content")

        response = self.client.post(
            reverse("notes:delete", kwargs={"slug": note.slug}), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cannot_edit_or_delete_others_notes(self):
        self.client.login(username="testuser1", password="12345")
        note = Note.objects.create(
            title="Test Note", text="Test Note content", author=self.user2
        )

        note_data = {"title": "Updated Note", "text": "Updated content"}
        response = self.client.post(
            reverse("notes:edit", kwargs={"slug": note.slug}),
            data=note_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 404)
        note.refresh_from_db()
        self.assertEqual(note.title, "Test Note")
        self.assertEqual(note.text, "Test Note content")

        response = self.client.post(
            reverse("notes:delete", kwargs={"slug": note.slug}), follow=True
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Note.objects.count(), 1)
