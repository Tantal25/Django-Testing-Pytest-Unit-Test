from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from pytils.translit import slugify
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NOTE_TITLE = 'Заголовок 2'
    NOTE_SLUG = 'note-slug'
    NOTE_ADD_REVERSE = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Василий Петрович')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {'title': cls.NOTE_TITLE,
                         'text': cls.NOTE_TEXT,
                         'slug': cls.NOTE_SLUG}

    def test_anonymous_user_cant_create_note(self):
        """Тест на невозможность анонимного пользователя создать заметку."""
        login_url = reverse('users:login')
        response = self.client.post(self.NOTE_ADD_REVERSE, data=self.form_data)
        expected_url = f'{login_url}?next={self.NOTE_ADD_REVERSE}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """Тест на возможность авторизованного пользователя создать заметку."""
        response = self.auth_client.post(
            self.NOTE_ADD_REVERSE, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.text, self.NOTE_TEXT)
        self.assertEqual(new_note.title, self.NOTE_TITLE)
        self.assertEqual(new_note.author, self.author)

    def test_not_unique_slug(self):
        """Тест на невозможность создать две заметки с одинаковым слагом."""
        note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug', author=self.author)
        self.form_data['slug'] = note.slug
        response = self.auth_client.post(
            self.NOTE_ADD_REVERSE, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Тест на заполнение пустого слага через транслит"""
        self.form_data.pop('slug')
        response = self.auth_client.post(
            self.NOTE_ADD_REVERSE, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст комментария'
    NEW_NOTE_TEXT = 'Обновлённый комментарий'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Виталий Игнорович')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок', text=cls.NOTE_TEXT, author=cls.author)
        cls.note_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {'text': cls.NEW_NOTE_TEXT, 'title': 'Новый заголовок'}

    def test_author_can_delete_note(self):
        """Тест на возможность удаления заметки автором."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Тест на невозможность удаления заметки другим пользователем."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        """Тест на возможность редактирования заметки автором."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        """Тест на невозможность изменения заметки другим пользователем."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
