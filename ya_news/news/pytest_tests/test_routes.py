import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from news.models import News, Comment


NEWS_EDIT = "news:edit"
NEWS_DELETE = "news:delete"
NEWS_HOME = "news:home"
NEWS_DETAIL = "news:detail"


@pytest.fixture
def user_fixture(db):
    return User.objects.create_user(username="testuser", password="12345")


@pytest.fixture
def another_user_fixture(db):
    return User.objects.create_user(username="testuser2", password="12345")


@pytest.fixture
def news_fixture(db):
    return News.objects.create(title="Test News", text="Test News content")


@pytest.fixture
def comment_fixture(db, news_fixture, user_fixture):
    return Comment.objects.create(
        news=news_fixture, author=user_fixture, text="Test Comment"
    )


@pytest.mark.django_db
def test_anonymous_user_access(client):
    response = client.get(reverse(NEWS_HOME))
    assert response.status_code == 200


@pytest.mark.django_db
def test_anonymous_user_cannot_edit_comment(
    client, user_fixture, news_fixture, comment_fixture
):
    comment = comment_fixture
    edit_response = client.get(reverse(NEWS_EDIT, kwargs={"pk": comment.pk}))
    assert edit_response.status_code == 302


@pytest.mark.django_db
def test_anonymous_user_cannot_delete_comment(
    client, user_fixture, news_fixture, comment_fixture
):
    comment = comment_fixture
    delete_response = client.get(
        reverse(NEWS_DELETE, kwargs={"pk": comment.pk})
    )
    assert delete_response.status_code == 302


@pytest.mark.django_db
def test_user_cannot_edit_or_delete_other_comments(
    client, user_fixture, another_user_fixture, comment_fixture
):
    client.login(username=another_user_fixture.username, password="12345")
    comment = comment_fixture

    edit_response = client.get(reverse(NEWS_EDIT, kwargs={"pk": comment.pk}))
    delete_response = client.get(
        reverse(NEWS_DELETE, kwargs={"pk": comment.pk})
    )

    assert edit_response.status_code == 404
    assert delete_response.status_code == 404


@pytest.mark.django_db
def test_detail_route_availability(client, news_fixture):
    news = news_fixture
    response = client.get(reverse(NEWS_DETAIL, kwargs={"pk": news.pk}))
    assert response.status_code == 200
