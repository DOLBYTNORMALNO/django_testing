import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from news.models import News, Comment


@pytest.mark.django_db
def test_anonymous_user_access(client):
    response = client.get(reverse("news:home"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_anonymous_user_cannot_edit_or_delete_comment(client):
    user = User.objects.create_user(username="testuser", password="12345")
    news = News.objects.create(title="Test News", text="Test News content")
    comment = Comment.objects.create(
        news=news, author=user, text="Test Comment"
    )
    edit_response = client.get(reverse("news:edit", kwargs={"pk": comment.pk}))
    delete_response = client.get(
        reverse("news:delete", kwargs={"pk": comment.pk})
    )
    assert edit_response.status_code == 302
    assert delete_response.status_code == 302


@pytest.mark.django_db
def test_user_cannot_edit_or_delete_other_comments(client):
    user1 = User.objects.create_user(username="testuser", password="12345")
    user2 = User.objects.create_user(username="otheruser", password="12345")
    client.login(username="otheruser", password="12345")
    news = News.objects.create(title="Test News", text="Test News content")
    comment = Comment.objects.create(
        news=news, author=user1, text="Test Comment"
    )
    edit_response = client.get(reverse("news:edit", kwargs={"pk": comment.pk}))
    delete_response = client.get(
        reverse("news:delete", kwargs={"pk": comment.pk})
    )
    assert edit_response.status_code == 404
    assert delete_response.status_code == 404
