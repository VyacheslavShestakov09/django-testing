from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    HOME_URL = reverse('notes:home')
    LOGIN_URL = reverse('users:login')
    LOGOUT_URL = reverse('users:logout')
    SIGNUP_URL = reverse('users:signup')
    ADD_URL = reverse('notes:add')
    LIST_URL = reverse('notes:list')
    SUCCESS_URL = reverse('notes:success')

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
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_pages_for_anon_user(self):
        """Тест доступности страниц для неавториз. польз."""
        urls = (
            self.HOME_URL,
            self.LOGIN_URL,
            self.LOGOUT_URL,
            self.SIGNUP_URL,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_for_auth_user(self):
        """Тест доступности страниц для авторизованного пользователя"""
        self.client.login(username='username', password='password')
        urls = (
            self.ADD_URL,
            self.LIST_URL,
            self.SUCCESS_URL,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_for_author_and_reader(self):
        """Тест доступа к страницам заметки для автора и читателя"""
        urls = (
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        users_status = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_status:
            self.client.force_login(user)
            for url in urls:
                with self.subTest(user=user.username, url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_anon_user(self):
        """Тест редиректа анонимных пользователей"""
        urls = (
            self.detail_url,
            self.edit_url,
            self.delete_url,
            self.ADD_URL,
            self.LIST_URL,
            self.SUCCESS_URL,
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
