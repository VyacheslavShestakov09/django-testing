from http import HTTPStatus

from django.urls import reverse

from news.models import Comment


def test_anon_comment(client, news):
    """Анонимный пользователь не может отправить комментарий
    и перенаправляется на вход
    """
    url = reverse('news:detail', args=(news.pk,))
    response = client.post(url, {'text': 'Тест'})
    login_url = reverse('users:login')
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(login_url)


def test_user_comment(author_client, news):
    """Авторизованный пользователь может комментировать"""
    url = reverse('news:detail', args=(news.pk,))
    text = 'Новый комментарий'
    response = author_client.post(url, {'text': text})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.filter(text=text).exists()


def test_comment_badwords(author_client, news):
    """Комментарий с запрещёнными словами не проходит валидацию"""
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, {'text': 'редиска'})
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    assert 'text' in response.context['form'].errors


def test_author_update_comment(author_client, comment):
    """Автор может обновить свой комментарий"""
    edit_url = reverse('news:edit', args=(comment.pk,))
    new_text = 'Обновлённый текст'
    response = author_client.get(edit_url)
    assert response.status_code == HTTPStatus.OK
    response = author_client.post(edit_url, {'text': new_text})
    comment.refresh_from_db()
    assert comment.text == new_text


def test_author_delete_comment(author_client, comment):
    """Автор может удалить свой комментарий"""
    delete_url = reverse('news:delete', args=(comment.pk,))
    response = author_client.post(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_reader_not_edit_comment(reader_client, comment):
    """Пользователь не может редактировать чужие комментарии"""
    edit_url = reverse('news:edit', args=(comment.pk,))
    response = reader_client.get(edit_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    original_text = comment.text
    response = reader_client.post(edit_url, {'text': 'text'})
    comment.refresh_from_db()
    assert comment.text == original_text
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_reader_not_delete_comment(reader_client, comment):
    """Другой пользователь не может удалить комментарий"""
    delete_url = reverse('news:delete', args=(comment.pk,))
    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()
