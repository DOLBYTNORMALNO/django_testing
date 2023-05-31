from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()
# Но в settings нет никакого AUTH_USER_MODE,
# что имеется ввиду?


class ContentTest(TestCase):
    NOTES_LIST = "notes:list"
    NOTES_ADD = "notes:add"
    NOTES_EDIT = "notes:edit"

    def setUp(self):
        self.client1 = Client()
        self.client2 = Client()
        self.user1 = User.objects.create_user(
            username="testuser1", password="12345"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", password="12345"
        )
        self.client1.login(username="testuser1", password="12345")
        self.client2.login(username="testuser2", password="12345")

    def test_note_in_list(self):
        note = Note.objects.create(
            title="Test Note", text="Test Note content", author=self.user1
        )
        response = self.client1.get(reverse(self.NOTES_LIST))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object_list"][0], note)

    def test_notes_list_does_not_contain_other_users_notes(self):
        note1 = Note.objects.create(
            title="Test Note 1", text="Test Note content", author=self.user1
        )
        note2 = Note.objects.create(
            title="Test Note 2", text="Test Note content", author=self.user2
        )
        response = self.client1.get(reverse(self.NOTES_LIST))
        self.assertEqual(response.status_code, 200)
        self.assertIn(note1, response.context["object_list"])
        self.assertNotIn(note2, response.context["object_list"])

    def test_create_edit_page_has_form(self):
        note = Note.objects.create(
            title="Test Note", text="Test Note content", author=self.user1
        )
        response = self.client1.get(reverse(self.NOTES_ADD))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("form" in response.context)

        response = self.client1.get(
            reverse(self.NOTES_EDIT, kwargs={"slug": note.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("form" in response.context)
