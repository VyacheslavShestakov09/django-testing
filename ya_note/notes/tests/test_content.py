from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNoteListContent(TestCase):
    """Тесты контента страницы со списком заметок"""
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор')
        cls.user = User.objects.create_user(username='Пользователь')
        cls.note = Note.objects.create(
            title='test note',
            text='text',
            slug='test-slug',
            author=cls.author
        )

    def test_notes_content(self):
        watch_notes = (
            (self.author, True),
            (self.user, False),
        )
        for user, expected_result in watch_notes:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(self.LIST_URL)
                self.assertIs(
                    self.note in response.context['object_list'],
                    expected_result
                )


class TestNoteFormContent(TestCase):
    """Тесты наличия форм на страницах создания/редактирования"""
    ADD_URL = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор')
        cls.note = Note.objects.create(
            title='test note',
            text='text',
            slug='test-slug',
            author=cls.author
        )
        cls.EDIT_URL = reverse('notes:edit', args=(cls.note.slug,))

    def test_forms(self):
        urls = (self.ADD_URL, self.EDIT_URL)
        self.client.force_login(self.author)
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIsInstance(response.context['form'], NoteForm)
