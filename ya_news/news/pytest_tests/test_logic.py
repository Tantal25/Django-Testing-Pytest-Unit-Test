from pytest_django.asserts import assertRedirects, assertFormError
import pytest
from http import HTTPStatus

from django.urls import reverse

from news.models import Comment
from news.forms import WARNING, BAD_WORDS


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, detail_reverse):
    """Тест на невозможность создания комментария анонимным пользователем."""
    response = client.post(detail_reverse, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={detail_reverse}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author_client, author, form_data, detail_reverse
):
    """Тест на создание комментария авторизированным пользователем."""
    response = author_client.post(detail_reverse, data=form_data)
    assertRedirects(response, detail_reverse + '#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


def test_user_cant_use_bad_words(author_client, detail_reverse):
    """Тест на применение запрещенных слов."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_reverse, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(
    author_client, form_data, comment, edit_reverse, detail_reverse
):
    """Тест на возможность редактирования комментария автором."""
    response = author_client.post(edit_reverse, form_data)
    assertRedirects(response, detail_reverse + '#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_author_can_delete_note(author_client, delete_reverse, detail_reverse):
    """Тест на возможность удаления комментария автором."""
    response = author_client.post(delete_reverse)
    assertRedirects(response, detail_reverse + '#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_edit_note(
    not_author_client, form_data, news, comment, edit_reverse
):
    """Тест на невозможность редактирования комментария не автором."""
    response = not_author_client.post(edit_reverse, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    note_from_db = Comment.objects.get(id=news.id)
    assert comment.text == note_from_db.text


def test_other_user_cant_delete_note(not_author_client, delete_reverse):
    """Тест на невозможность удаления комментария не автором."""
    response = not_author_client.post(delete_reverse)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
