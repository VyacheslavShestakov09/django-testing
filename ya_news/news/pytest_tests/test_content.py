from django.conf import settings
import pytest

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count_homepage(client, excess_news, home_url):
    """Количество новостей на главной странице"""
    response = client.get(home_url)
    assert 'object_list' in response.context
    news_count = len(response.context['object_list'])
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, excess_news, home_url):
    """Новости отсортированы от свежей к старой"""
    response = client.get(home_url)
    assert 'object_list' in response.context
    news_list = response.context['object_list']
    dates = [news.date for news in news_list]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(client, news, comments_create, detail_url):
    """Комментарии отсортированы от старого к новому"""
    response = client.get(detail_url)
    assert 'news' in response.context
    comments = response.context['news'].comment_set.all()
    created_times = [comment.created for comment in comments]
    assert created_times == sorted(created_times)


@pytest.mark.django_db
def test_comment_form_anon(client, news, detail_url):
    """Анон не видит форму коммента"""
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_comment_form(reader_client, news, detail_url):
    """Авторизованный пользователь видит форму коммента"""
    response = reader_client.get(detail_url)
    assert 'form' in response.context
    form = response.context['form']
    assert isinstance(form, CommentForm)
