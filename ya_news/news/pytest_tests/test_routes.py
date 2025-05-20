from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        lazy_fixture('home_url'),
        lazy_fixture('detail_url'),
        lazy_fixture('login_url'),
        lazy_fixture('signup_url'),
        lazy_fixture('logout_url'),
    )
)
def test_public_pages(client, url):
    """Проверка общедоступных страниц"""
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'client, expected_status',
    (
        (lazy_fixture('author_client'), HTTPStatus.OK),
        (lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.parametrize(
    'url',
    (
        lazy_fixture('edit_comment_url'),
        lazy_fixture('delete_comment_url'),
    )
)
def test_comment_edit_delete_availability(
    client,
    url,
    expected_status
):
    """Доступ к редактированию/удалению комментариев"""
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        lazy_fixture('edit_comment_url'),
        lazy_fixture('delete_comment_url'),
    )
)
def test_anon_redirect(client, url, login_url):
    """Редирект для анонимных пользователей"""
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
