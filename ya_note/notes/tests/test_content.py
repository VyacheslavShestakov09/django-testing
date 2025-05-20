from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNoteListContent(TestCase):
    """Тесты контента страницы со списком заметок"""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор')
        cls.user = User.objects.create_user(username='Пользователь')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='test note',
            text='text',
            slug='test-slug',
            author=cls.author
        )
        cls.list_url = reverse('notes:list')

    def test_notes_content(self):
        """Тест отображения заметок автору и юзеру"""
        watch_notes = (
            (self.author_client, True),
            (self.user_client, False),
        )
        for client, expected_result in watch_notes:
            with self.subTest(client=client):
                response = client.get(self.list_url)
                self.assertIs(
                    self.note in response.context['object_list'],
                    expected_result
                )


class TestNoteFormContent(TestCase):
    """Тесты наличия форм на страницах создания/редактирования"""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='test note',
            text='text',
            slug='test-slug',
            author=cls.author
        )
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_forms(self):
        """Тестируем наличие форм"""
        urls = (self.add_url, self.edit_url)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIsInstance(response.context['form'], NoteForm)
