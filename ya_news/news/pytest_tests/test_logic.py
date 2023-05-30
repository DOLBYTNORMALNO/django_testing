import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from news.models import News, Comment


FORBIDDEN_WORDS = ["bad_word1", "bad_word2", "bad_word3"]


@pytest.mark.django_db
def test_anonymous_user_cannot_comment(client):
    news = News.objects.create(title="Test News", text="Test News content")
    comment_count = Comment.objects.count()
    response = client.post(
        reverse("news:detail", kwargs={"pk": news.pk}),
        data={"text": "Test Comment"},
    )
    assert response.status_code == 302
    assert Comment.objects.count() == comment_count


@pytest.mark.django_db
def test_authorized_user_can_comment(client):
    user = User.objects.create_user(username="testuser", password="12345")
    news = News.objects.create(title="Test News", text="Test News content")
    client.login(username="testuser", password="12345")
    response = client.post(
        reverse("news:detail", kwargs={"pk": news.pk}),
        data={"text": "Test Comment"},
    )
    assert response.status_code == 302
    assert Comment.objects.count() == Comment.objects.count()


@pytest.mark.django_db
def test_comment_with_forbidden_words_not_published(client):
    user = User.objects.create_user(username="testuser", password="12345")
    news = News.objects.create(title="Test News", text="Test News content")
    client.login(username="testuser", password="12345")
    response = client.post(
        reverse("news:detail", kwargs={"pk": news.pk}),
        data={
            "text": f"Test Comment with forbidden word {FORBIDDEN_WORDS[0]}"
        },
    )
    assert response.status_code == 302


@pytest.mark.django_db
def test_authorized_user_can_edit_own_comment(client):
    user = User.objects.create_user(username="testuser", password="12345")
    news = News.objects.create(title="Test News", text="Test News content")
    comment = Comment.objects.create(
        news=news, author=user, text="Test Comment"
    )
    client.login(username="testuser", password="12345")
    new_comment_text = "Updated Comment"
    response = client.post(
        reverse("news:edit", kwargs={"pk": comment.pk}),
        data={"text": new_comment_text},
    )
    comment.refresh_from_db()
    assert comment.text == new_comment_text


@pytest.mark.django_db
def test_authorized_user_cannot_edit_or_delete_others_comments(client):
    user1 = User.objects.create_user(username="testuser1", password="12345")
    user2 = User.objects.create_user(username="testuser2", password="12345")
    news = News.objects.create(title="Test News", text="Test News content")
    comment = Comment.objects.create(
        news=news, author=user1, text="Test Comment"
    )
    client.login(username="testuser2", password="12345")

    new_comment_text = "Unauthorized Update Attempt"
    response = client.post(
        reverse("news:edit", kwargs={"pk": comment.pk}),
        data={"text": new_comment_text},
    )
    comment.refresh_from_db()
    assert comment.text != new_comment_text

    initial_count = Comment.objects.count()
    response = client.post(reverse("news:delete", kwargs={"pk": comment.pk}))
    assert Comment.objects.count() == initial_count
