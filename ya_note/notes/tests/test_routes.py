from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='username',
            password='password'
        )
        cls.reader = User.objects.create_user(
            username='reader',
            password='readerpass'
        )
        cls.note = Note.objects.create(
            title='Заметка',
            text='text',
            slug='test-slug',
            author=cls.author
        )

    def test_home_page(self):
        """Тест доступности главной страницы для всех"""
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_show_notes(self):
        """Тест доступности списка заметок для авторизованного пользователя"""
        self.client.login(username='username', password='password')
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('object_list', response.context)
        self.assertEqual(len(response.context['object_list']), 1)

    def test_success_page(self):
        """Тест доступности страницы успешного добавлении заметки"""
        self.client.login(username='username', password='password')
        url = reverse('notes:success')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_add_notes(self):
        """Тест доступности добавления новой заметки
        авторизованному пользователю
        """
        self.client.login(username='username', password='password')
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_note_author(self):
        """Тест доступности страницы заметки автора"""
        self.client.login(username='username', password='password')
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_note_reader(self):
        """Страница заметки недоступна другим пользователям"""
        self.client.login(username='reader', password='readerpass')
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_anonymous(self):
        """Тест ридеректа для неавторизованных пользователей"""
        login_url = reverse('users:login')
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_auth_pages(self):
        """Тест проверки доступности страниц аутентификации для всех"""
        urls = (
            ('users:login', None),
            ('users:signup', None),
            ('users:logout', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
