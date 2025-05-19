from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreation(TestCase):
    """Тесты для создания заметок"""
    ADD_URL = reverse('notes:add')
    SUCCESS_URL = reverse('notes:success')

    @classmethod
    def setUpTestData(cls):
        cls.anon_client = Client()
        cls.author = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'test-slug'
        }

    def test_anon_creat_note(self):
        """Анонимный пользователь не может создать заметку"""
        initial_count = Note.objects.count()
        self.anon_client.post(self.ADD_URL, data=self.form_data)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_user_creat_note(self):
        """Авторизованный пользователь может создать заметку"""
        initial_count = Note.objects.count()
        response = self.auth_client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), initial_count + 1)
        note = Note.objects.last()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.author)

    def test_user_repeat_slug(self):
        """Нельзя создать две заметки с одинаковым slug"""
        Note.objects.all().delete()
        Note.objects.create(
            title='Заметка',
            text='Текст',
            slug=self.form_data['slug'],
            author=self.author
        )
        initial_count = Note.objects.count()
        response = self.auth_client.post(self.ADD_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form', response.context)
        self.assertFormError(
            response.context['form'],
            'slug',
            [f"{self.form_data['slug']}{WARNING}"]
        )
        self.assertEqual(Note.objects.count(), initial_count)


class TestNoteEditDelete(TestCase):
    """Тесты редактирования и удаления заметок"""
    SUCCESS_URL = reverse('notes:success')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-slug',
            author=cls.author
        )
        cls.EDIT_URL = reverse('notes:edit', args=(cls.note.slug,))
        cls.DELETE_URL = reverse('notes:delete', args=(cls.note.slug,))
        cls.new_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_author_delete_note(self):
        """Автор может удалить свою заметку"""
        initial_count = Note.objects.count()
        response = self.author_client.delete(self.DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), initial_count - 1)

    def test_user_delete_note(self):
        """Пользователь не может удалить чужую заметку"""
        initial_count = Note.objects.count()
        response = self.reader_client.delete(self.DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_author_edit_note(self):
        """Автор может редактировать свою заметку"""
        response = self.author_client.post(self.EDIT_URL, data=self.new_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.new_data['title'])
        self.assertEqual(note.text, self.new_data['text'])
        self.assertEqual(note.slug, self.new_data['slug'])

    def test_user_not_edit_note(self):
        """Пользователь не может редактировать чужую заметку"""
        original_note = Note.objects.get(id=self.note.id)
        response = self.reader_client.post(self.EDIT_URL, data=self.new_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, original_note.title)
        self.assertEqual(updated_note.text, original_note.text)
        self.assertEqual(updated_note.slug, original_note.slug)
