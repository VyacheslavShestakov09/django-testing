from django.contrib.auth import get_user_model
from django.test import TestCase
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
        cls.note = Note.objects.create(
            title='test note',
            text='text',
            slug='test-slug',
            author=cls.author
        )

    def test_author_sees_own_notes(self):
        """Автор видит свои заметки в списке"""
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        self.assertIn('object_list', response.context)
        self.assertIn(self.note, response.context['object_list'])

    def test_user_doesnt_see_others_notes(self):
        """Пользователь не видит чужие заметки"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('notes:list'))
        self.assertIn('object_list', response.context)
        self.assertNotIn(self.note, response.context['object_list'])


class TestNoteFormContent(TestCase):
    """Тесты наличия форм на страницах создания/редактирования"""
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор')
        cls.note = Note.objects.create(
            title='test note',
            text='text',
            slug='test-slug',
            author=cls.author
        )

    def test_forms_availability(self):
        """Проверка наличия форм на страницах"""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
