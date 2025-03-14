import pytest
from django.conf import settings


@pytest.mark.django_db
def test_news_count_on_home_page(client, multiple_news, home_url):
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE, (
        f'На главной странице должно быть не более \
          {settings.NEWS_COUNT_ON_HOME_PAGE} новостей.'
    )


@pytest.mark.django_db
def test_news_order_on_home_page(client, multiple_news, home_url):
    response = client.get(home_url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    assert dates == sorted(dates, reverse=True), (
        'Новости на главной странице должны быть отсортированы'
        ' от самой свежей к самой старой.'
    )


@pytest.mark.django_db
def test_comments_order_on_news_detail_page(
    client, news, multiple_comments, news_detail_url
):
    response = client.get(news_detail_url)
    comments = response.context['news'].comment_set.all()
    created_times = [comment.created for comment in comments]
    assert created_times == sorted(created_times), (
        'Комментарии на странице новости должны быть отсортированы'
        ' от старых к новым.'
    )


@pytest.mark.django_db
def test_comment_form_availability_to_anonymous_user(
    client, news, news_detail_url
):
    response = client.get(news_detail_url)
    assert 'form' not in response.context, (
        'Анонимному пользователю не должна быть доступна форма'
        ' для отправки комментария.'
    )


@pytest.mark.django_db
def test_comment_form_availability_to_authenticated_user(
    client, news, author, news_detail_url
):
    client.force_login(author)
    response = client.get(news_detail_url)
    assert 'form' in response.context, (
        'Авторизованному пользователю должна быть доступна форма'
        ' для отправки комментария.'
    )
