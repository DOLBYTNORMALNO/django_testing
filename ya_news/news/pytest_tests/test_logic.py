import random
import pytest

from django.urls import reverse
from django.contrib.auth.models import User

from news.models import News, Comment
from news.forms import BAD_WORDS

NEWS_EDIT = "news:edit"
NEWS_DELETE = "news:delete"
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
def test_anonymous_user_cannot_comment(client, news_fixture):
    comment_count = Comment.objects.count()
    response = client.post(
        reverse(NEWS_DETAIL, kwargs={"pk": news_fixture.pk}),
        data={"text": "Test Comment"},
    )
    assert response.status_code == 302
    assert Comment.objects.count() == comment_count


@pytest.mark.django_db
def test_authorized_user_can_comment(client, user_fixture, news_fixture):
    client.login(username=user_fixture.username, password="12345")
    response = client.post(
        reverse(NEWS_DETAIL, kwargs={"pk": news_fixture.pk}),
        data={"text": "Test Comment"},
    )
    assert response.status_code == 302
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_comment_with_forbidden_words_not_published(
    client, user_fixture, news_fixture
):
    client.login(username=user_fixture.username, password="12345")
    response = client.post(
        reverse(NEWS_DETAIL, kwargs={"pk": news_fixture.pk}),
        data={
            "text": f"Test Comment with forbidden word { random.choice(BAD_WORDS)}"
        },
    )
    assert response.status_code == 200
    # Здесь почему то тесты задания работают диаметрально противоположно,
    # при нахождении запретного слова требуют вывод 200,
    # а при добавлении not требуют 302, но никак не 403, не понимаю, что не так
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_authorized_user_can_edit_own_comment(
    client, user_fixture, comment_fixture
):
    client.login(username=user_fixture.username, password="12345")
    new_comment_text = "Updated Comment"
    client.post(
        reverse(NEWS_EDIT, kwargs={"pk": comment_fixture.pk}),
        data={"text": new_comment_text},
    )
    comment_fixture.refresh_from_db()
    assert comment_fixture.text == new_comment_text


@pytest.mark.django_db
def test_authorized_user_cannot_edit_others_comments(
    client, user_fixture, another_user_fixture, comment_fixture
):
    client.login(username=another_user_fixture.username, password="12345")
    new_comment_text = "Unauthorized Update Attempt"
    client.post(
        reverse(NEWS_EDIT, kwargs={"pk": comment_fixture.pk}),
        data={"text": new_comment_text},
    )
    comment_fixture.refresh_from_db()
    assert comment_fixture.text != new_comment_text


@pytest.mark.django_db
def test_authorized_user_cannot_delete_others_comments(
    client, user_fixture, another_user_fixture, comment_fixture
):
    client.login(username=another_user_fixture.username, password="12345")
    initial_count = Comment.objects.count()
    client.post(reverse(NEWS_DELETE, kwargs={"pk": comment_fixture.pk}))
    assert Comment.objects.count() == initial_count
