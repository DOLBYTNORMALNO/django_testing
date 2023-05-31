import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from news.models import News, Comment
from django.conf import settings


NEWS_HOME = "news:home"
NEWS_DETAIL = "news:detail"


@pytest.fixture
def user_fixture(db):
    return User.objects.create_user(username="testuser", password="12345")


@pytest.fixture
def news_fixture():
    return [
        News.objects.create(
            title=f"Test News {i}",
            text=f"Test News content {i}",
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE)
    ]


@pytest.fixture
def comments_fixture(news_fixture, user_fixture):
    user = user_fixture
    news = news_fixture[0]
    return [
        Comment.objects.create(
            news=news, author=user, text=f"Test Comment {i}"
        )
        for i in range(5)
    ]


@pytest.mark.django_db
def test_home_page_news_count(client, news_fixture):
    response = client.get(reverse(NEWS_HOME))
    assert (
        len(response.context["object_list"])
        <= settings.NEWS_COUNT_ON_HOME_PAGE
    )


@pytest.mark.django_db
def test_news_order(client, news_fixture):
    response = client.get(reverse(NEWS_HOME))
    assert list(response.context["object_list"]) == list(
        News.objects.all().order_by("-date")[
            : settings.NEWS_COUNT_ON_HOME_PAGE
        ]
    )


@pytest.mark.django_db
def test_comments_order(client, comments_fixture):
    news = comments_fixture[0].news
    response = client.get(reverse(NEWS_DETAIL, kwargs={"pk": news.pk}))
    assert list(response.context["object"].comment_set.all()) == list(
        news.comment_set.all().order_by("created")
    )


@pytest.mark.django_db
def test_comment_form_availability(client, user_fixture, news_fixture):
    news = news_fixture[0]
    response = client.get(reverse(NEWS_DETAIL, kwargs={"pk": news.pk}))
    assert "form" not in response.context
    client.login(username=user_fixture.username, password="12345")
    response = client.get(reverse(NEWS_DETAIL, kwargs={"pk": news.pk}))
    assert "form" in response.context
