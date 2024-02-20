from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Василий Петрович')
        cls.reader = User.objects.create(username='Какой-то читатель')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.authorized_reader = Client()
        cls.authorized_reader.force_login(cls.reader)

    def test_pages_availability(self):
        """
        Тест на доступность главной страницы и страниц
        аутентификации для пользователей.
        """
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_availability_for_notes(self):
        """
        Тест на доступность страниц отдельной заметки,
        редактирования и удаления заметок для автора.
        """
        users_statuses = (
            (self.authorized_client, HTTPStatus.OK),
            (self.authorized_reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_authorized_user_availability_for_notes(self):
        """
        Тест на доступность страниц добавления заметки,
        списка заметок и страницы успешного действия для автора.
        """
        for name in ('notes:add', 'notes:success', 'notes:list'):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """Тест на редирект анонимных пользователей на страницу логина."""
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
