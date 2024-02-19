import pytest

from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_on_page_count(client, set_of_news, home_reverse):
    """Тест на количество новостей на одной странице."""
    response = client.get(home_reverse)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, set_of_news, home_reverse):
    """Тест на порядок новостей на странице."""
    response = client.get(home_reverse)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comment_order(set_of_comments):
    """Тест на порядок комментариев у новости."""
    all_timestamps = [comment.created for comment in set_of_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, detail_reverse):
    """Тест на отсутствие формы комментариев у анонимного пользователя."""
    response = client.get(detail_reverse)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, detail_reverse):
    """Тест на наличие формы комментариев у авторизированного пользователя."""
    response = author_client.get(detail_reverse)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
