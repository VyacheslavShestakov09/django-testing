from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from news.models import Comment, News


User = get_user_model()


@pytest.fixture(autouse=True)
def enable_db(db):
    """Разрешаем доступ к БД для всех тестов"""
    pass


@pytest.fixture
def author(django_user_model):
    """Создает автора комментариев"""
    return django_user_model.objects.create_user(username='Автор')


@pytest.fixture
def author_client(author, client):
    """Клиент автора комментариев"""
    client.force_login(author)
    return client


@pytest.fixture
def reader(django_user_model):
    """Создает обычного пользователя"""
    return django_user_model.objects.create_user(username='Читатель')


@pytest.fixture
def reader_client(reader, client):
    """Клиент обычного пользователя"""
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    """Создает тестовую новость"""
    return News.objects.create(
        title='Тестовая новость',
        text='Текст новости',
        date=timezone.now().date()
    )


@pytest.fixture
def create_eleven_news():
    """Создает 11 новостей с разными датами"""
    today = timezone.now().date()
    News.objects.bulk_create([
        News(
            title=f'Новость {index}',
            text='Текст',
            date=today - timedelta(days=index)
        ) for index in range(11)
    ])


@pytest.fixture
def create_comment_two(news, author):
    """Создает два комментария с разным временем создания"""
    for index in range(2):
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}',
            created=timezone.now() + timedelta(minutes=index)
        )


@pytest.fixture
def comment(news, author):
    """Создает один комментарий"""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
        created=timezone.now()
    )
