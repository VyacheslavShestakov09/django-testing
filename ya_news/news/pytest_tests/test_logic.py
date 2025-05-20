from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anon_comment(client, news, comment_form_data, detail_url, login_url):
    """Анонимный пользователь не может отправить комментарий
    и перенаправляется на вход
    """
    response = client.post(detail_url, data=comment_form_data)
    assert Comment.objects.count() == 0
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)


def test_user_comment(
        author_client,
        news,
        author,
        detail_url,
        comment_form_data
):
    """Авторизованный пользователь может комментировать"""
    response = author_client.post(detail_url, comment_form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == comment_form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_badwords(author_client, news, detail_url, bad_word):
    """Комментарий с запрещёнными словами не проходит валидацию"""
    response = author_client.post(detail_url, {'text': bad_word})
    assert Comment.objects.count() == 0
    form = response.context['form']
    assertFormError(
        form,
        'text',
        WARNING
    )
    assert response.status_code == HTTPStatus.OK


def test_author_update_comment(
    author_client,
    comment,
    edit_comment_url,
    news,
    author,
    comment_form_data,
):
    """Автор может обновить свой комментарий"""
    author_client.post(edit_comment_url, data=comment_form_data)
    comment.refresh_from_db()
    assert comment.text == comment_form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_author_delete_comment(author_client, comment, delete_comment_url):
    """Автор может удалить свой комментарий"""
    response = author_client.post(delete_comment_url)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=comment.pk).exists()
    assert Comment.objects.count() == 0


def test_reader_not_edit_comment(
    reader_client,
    comment,
    edit_comment_url,
    author,
    news,
    comment_form_data
):
    """Пользователь не может редактировать чужие комментарии"""
    response = reader_client.get(edit_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    response = reader_client.post(edit_comment_url, comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == comment.text
    assert comment.author == author
    assert comment.news == news


def test_reader_not_delete_comment(
    reader_client,
    comment,
    delete_comment_url
):
    """Другой пользователь не может удалить комментарий"""
    response = reader_client.post(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()
    assert Comment.objects.count() == 1
