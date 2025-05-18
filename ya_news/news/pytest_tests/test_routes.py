import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_home_page(client):
    """Доступ главной страницы анонимному пользователю"""
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_detail_page(client, news):
    """Доступ к странице новости анонимному пользователю"""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert response.status_code == 200


def test_comment_edit_delete_author(author_client, comment):
    """Доступ страниц редактирования и удаления для автора"""
    urls = [
        reverse('news:edit', kwargs={'pk': comment.pk}),
        reverse('news:delete', kwargs={'pk': comment.pk}),
    ]
    for url in urls:
        response = author_client.get(url)
        assert response.status_code == 200


def test_anonymous_redirected(client, comment):
    """Проверяем редирект анонима на страницу логина"""
    urls = [
        reverse('news:edit', kwargs={'pk': comment.pk}),
        reverse('news:delete', kwargs={'pk': comment.pk}),
    ]
    for url in urls:
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url}'
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == redirect_url


def test_comments(reader_client, comment):
    """Тест запрета доступа к чужим комментариям"""
    urls = [
        reverse('news:edit', kwargs={'pk': comment.pk}),
        reverse('news:delete', kwargs={'pk': comment.pk}),
    ]
    for url in urls:
        response = reader_client.get(url)
        assert response.status_code == 404


def test_auth_pages_availability(client):
    """Страницы регистрации, входа и выхода доступны анонимам"""
    urls = [
        reverse('users:login'),
        reverse('users:signup'),
        reverse('users:logout'),
    ]
    for url in urls:
        response = client.get(url)
        assert response.status_code == 200
