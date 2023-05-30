import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from news.models import News, Comment
import datetime
from django.utils import timezone


@pytest.mark.django_db
def test_home_page_news_count(client):
    for i in range(15):
        News.objects.create(
            title=f"Test News {i}", text=f"Test News content {i}"
        )
    response = client.get(reverse("news:home"))
    assert len(response.context["object_list"]) <= 10


@pytest.mark.django_db
def test_news_order(client):
    current_time = timezone.now()
    [
        News.objects.create(
            title=f"Test News {i}",
            text=f"Test News content {i}",
            date=current_time - datetime.timedelta(days=i),
        )
        for i in range(5)
    ]
    response = client.get(reverse("news:home"))
    assert list(response.context["object_list"]) == list(News.objects.all())


@pytest.mark.django_db
def test_comments_order(client):
    user = User.objects.create_user(username="testuser", password="12345")
    news = News.objects.create(title="Test News", text="Test News content")
    comments = [
        Comment.objects.create(
            news=news, author=user, text=f"Test Comment {i}"
        )
        for i in range(5)
    ]
    response = client.get(reverse("news:detail", kwargs={"pk": news.pk}))
    assert list(response.context["object"].comment_set.all()) == comments


@pytest.mark.django_db
def test_comment_form_availability(client):
    User.objects.create_user(username="testuser", password="12345")
    news = News.objects.create(title="Test News", text="Test News content")
    response = client.get(reverse("news:detail", kwargs={"pk": news.pk}))
    assert "form" not in response.context
    client.login(username="testuser", password="12345")
    response = client.get(reverse("news:detail", kwargs={"pk": news.pk}))
    assert "form" in response.context
