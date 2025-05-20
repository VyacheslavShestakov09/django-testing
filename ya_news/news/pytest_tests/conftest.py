from datetime import timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone
from django.urls import reverse

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def author(django_user_model):
    """Создает автора комментариев"""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    """Клиент автора комментариев"""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader(django_user_model):
    """Создает обычного пользователя"""
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader):
    """Клиент обычного пользователя"""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    """Создает тестовую новость с дефолтными параметрами"""
    return News.objects.create(
        title='Тестовая новость',
        text='Текст'
    )


@pytest.fixture
def excess_news():
    """Создаёт новостей на 1 больше, чем разрешено на главной странице"""
    today = timezone.now().date()
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        News.objects.create(
            title=f'Новость {index}',
            text='Текст',
            date=today - timedelta(days=index)
        )


@pytest.fixture
def comments_create(news, author):
    """Создает 10 комментариев с разным временем"""
    for index in range(10):
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}',
            created=timezone.now() + timedelta(minutes=index)
        )


@pytest.fixture
def comment(news, author):
    """Создает один комментарий с дефолтными параметрами"""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст'
    )


@pytest.fixture
def home_url():
    """URL главной страницы"""
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    """URL страницы новости"""
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def login_url():
    """URL логина"""
    return reverse('users:login')


@pytest.fixture
def signup_url():
    """URL страницы регистрации"""
    return reverse('users:signup')


@pytest.fixture
def logout_url():
    """URL страницы выхода"""
    return reverse('users:logout')


@pytest.fixture
def edit_comment_url(comment):
    """URL редактирования коммента"""
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def delete_comment_url(comment):
    """URL удаления коммента"""
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def comment_form_data():
    """Форма комментария с текстом"""
    return {'text': 'Тест'}
