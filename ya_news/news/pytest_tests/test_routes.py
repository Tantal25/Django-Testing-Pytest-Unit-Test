from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args',
    (
        ('users:login', None,),
        ('users:logout', None,),
        ('users:signup', None,),
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('pk_for_args')),
    )
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name, args):
    """
    Тест на доступность страницы аутентификации, регистрации
    и главной страницы для анонимного пользователя.
    """
    response = client.get(reverse(name, args=args))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_edit_and_delete_comment_pages_availability_for_different_users(
    parametrized_client, name, expected_status, pk_for_comment_args
):
    """
    Тест на доступность страниц редактирования и удаления
    для разных пользователей.
    """
    response = parametrized_client.get(
        reverse(name, args=(pk_for_comment_args)))
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'current_url',
    ('news:edit', 'news:delete'),
)
@pytest.mark.django_db
def test_anonymous_user_redirects(
    client, pk_for_comment_args, current_url
):
    """Тест на перенаправление анонимных пользователей на страницу логина."""
    login_url = reverse('users:login')
    url = reverse(current_url, args=(pk_for_comment_args))
    response = client.get(url)
    expected_url = (f"{login_url}?next={url}")
    assertRedirects(response, expected_url)
