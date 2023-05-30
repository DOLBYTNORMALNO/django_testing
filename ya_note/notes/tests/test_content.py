from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()


class ContentTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username="testuser1", password="12345"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", password="12345"
        )

    def test_note_in_list(self):
        self.client.login(username="testuser1", password="12345")
        note = Note.objects.create(
            title="Test Note", text="Test Note content", author=self.user1
        )

        response = self.client.get(reverse("notes:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object_list"][0], note)

    def test_notes_list_does_not_contain_other_users_notes(self):
        self.client.login(username="testuser1", password="12345")
        note1 = Note.objects.create(
            title="Test Note 1", text="Test Note content", author=self.user1
        )
        note2 = Note.objects.create(
            title="Test Note 2", text="Test Note content", author=self.user2
        )

        response = self.client.get(reverse("notes:list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(note1, response.context["object_list"])
        self.assertNotIn(note2, response.context["object_list"])

    def test_create_edit_page_has_form(self):
        self.client.login(username="testuser1", password="12345")
        note = Note.objects.create(
            title="Test Note", text="Test Note content", author=self.user1
        )

        response = self.client.get(reverse("notes:add"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("form" in response.context)

        response = self.client.get(
            reverse("notes:edit", kwargs={"slug": note.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("form" in response.context)
