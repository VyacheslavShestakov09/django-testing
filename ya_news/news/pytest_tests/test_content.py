from django.conf import settings
from django.urls import reverse


def test_news_count_homepage(client, create_eleven_news):
    """Количество новостей на главной странице"""
    response = client.get(reverse('news:home'))
    news_count = len(response.context['object_list'])
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, create_eleven_news):
    """Новости отсортированы от свежей к старой"""
    response = client.get(reverse('news:home'))
    news_list = response.context['object_list']
    dates = [news.date for news in news_list]
    assert dates == sorted(dates, reverse=True)


def test_comments_order(client, news, create_comment_two):
    """Комментарии отсортированы от старого к новому"""
    response = client.get(reverse('news:detail', args=(news.pk,)))
    comments = response.context['news'].comment_set.all()
    created_times = [comment.created for comment in comments]
    assert created_times == sorted(created_times)


def test_comment_form_anon(client, news):
    """Анон не видит форму коммента"""
    response = client.get(reverse('news:detail', args=(news.pk,)))
    assert 'form' not in response.context


def test_authorized_comment_form(reader_client, news):
    """Авторизованный пользователь видит форму коммента"""
    response = reader_client.get(reverse('news:detail', args=(news.pk,)))
    assert 'form' in response.context
