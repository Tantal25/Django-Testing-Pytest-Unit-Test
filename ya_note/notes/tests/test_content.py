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
        cls.second_note = Note.objects.create(
            title='Заголовок2',
            text='Текст2',
            author=cls.second_author)
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)

    def test_notes_check(self):
        """
        Тест проверяющий передачу отдельной заметки в словаре context
        и отсутствие заметок других пользователей в списке другого.
        """
        response = self.auth_client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, 1)

    def test_authorized_client_has_form(self):
        """Тест на появление формы заметки у авторизированного пользователя."""
        self.client.force_login(self.author)
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=args))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
