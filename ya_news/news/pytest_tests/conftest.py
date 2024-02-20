from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
import pytest

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def set_of_news():
    today = datetime.today()
    News.objects.bulk_create(
        News(title=f'Новость {index}',
             text='Просто текст.',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1))


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        text='Текст комментария',
        author=author,
        news=news
    )


@pytest.fixture
def set_of_comments(news, author):
    today = datetime.today()
    Comment.objects.bulk_create(
        Comment(text=f'Текст комментария {index}',
                news=news,
                author=author,
                created=today - timedelta(hours=index))
        for index in range(5))


@pytest.fixture
def pk_for_args(news):
    return (news.pk,)


@pytest.fixture
def pk_for_comment_args(comment):
    return (comment.pk,)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст комментария',
    }


@pytest.fixture
def home_reverse():
    return reverse('news:home')


@pytest.fixture
def detail_reverse(pk_for_args):
    return reverse('news:detail', args=pk_for_args)


@pytest.fixture
def edit_reverse(pk_for_comment_args):
    return reverse('news:edit', args=pk_for_comment_args)


@pytest.fixture
def delete_reverse(pk_for_comment_args):
    return reverse('news:delete', args=pk_for_comment_args)
