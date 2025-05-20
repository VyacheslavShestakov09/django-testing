from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Атвор')
        cls.reader = User.objects.create_user(username='Читатель')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заметка',
            text='text',
            slug='test-slug',
            author=cls.author
        )
        cls.home_url = reverse('notes:home')
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')
        cls.add_url = reverse('notes:add')
        cls.list_url = reverse('notes:list')
        cls.success_url = reverse('notes:success')
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_pages_for_anon_user(self):
        """Тест доступности страниц для неавториз. польз."""
        urls = (
            self.home_url,
            self.login_url,
            self.logout_url,
            self.signup_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_for_auth_user(self):
        """Тест доступности страниц для авторизованного пользователя"""
        urls = (
            self.add_url,
            self.list_url,
            self.success_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_for_author_and_reader(self):
        """Тест доступа к страницам заметки для автора и читателя"""
        urls = (
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        client_status = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for client, status in client_status:
            for url in urls:
                with self.subTest(client=client, url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_anon_user(self):
        """Тест редиректа анонимных пользователей"""
        urls = (
            self.detail_url,
            self.edit_url,
            self.delete_url,
            self.add_url,
            self.list_url,
            self.success_url,
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
