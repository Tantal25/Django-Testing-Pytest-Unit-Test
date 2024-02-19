from http import HTTPStatus

from pytest_django.asserts import assertRedirects
import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_home_and_detail_page_availability_for_anonymous_user(
        client, home_reverse, detail_reverse
):
    """
    Тест на доступность главной страницы и
    страницы отдельной новости для анонимного пользователя.
    """
    home_response = client.get(home_reverse)
    detail_response = client.get(detail_reverse)
    assert home_response.status_code == HTTPStatus.OK
    assert detail_response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('users:login', 'users:logout', 'users:signup',)
)
def test_pages_availability_for_anonymous_user(client, name):
    """
    Тест на доступность страницы аутентификации и
    регистрации для анонимного пользователя.
    """
    response = client.get(reverse(name))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
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
    url = reverse(name, args=(pk_for_comment_args))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
def test_anonymous_user_redirects(
    client, edit_reverse, delete_reverse
):
    """Тест на перенаправление анонимных пользователей на страницу логина."""
    login_url = reverse('users:login')
    edit_response = client.get(edit_reverse)
    expected_edit_url = (f"{login_url}?next={edit_reverse}")
    assertRedirects(edit_response, expected_edit_url)
    delete_response = client.get(delete_reverse)
    expected_delete_url = (f"{login_url}?next={delete_reverse}")
    assertRedirects(delete_response, expected_delete_url)
