from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestHomePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Василий Петрович')
        cls.second_author = User.objects.create(username='Петровий Василич')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author)
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.second_auth_client = Client()
        cls.second_auth_client.force_login(cls.second_author)

    def test_notes_check(self):
        """
        Тест проверяющий передачу отдельной заметки в словаре context
        и отсутствие заметок других пользователей в списке другого.
        """
        client_note_status = (
            (self.auth_client, True),
            (self.second_auth_client, False),
        )
        for exact_client, note_in_list in client_note_status:
            with self.subTest(exact_client=exact_client,
                              note_in_list=note_in_list):
                response = exact_client.get(reverse('notes:list'))
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, note_in_list)

    def test_authorized_client_has_form(self):
        """Тест на появление формы заметки у авторизированного пользователя."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                response = self.auth_client.get(reverse(name, args=args))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
