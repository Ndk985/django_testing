import pytest
from django.contrib.auth import get_user_model
from news.models import News, Comment
from datetime import datetime, timedelta
from django.urls import reverse

User = get_user_model()


@pytest.fixture
def author():
    """Фикстура для создания автора комментария."""
    return User.objects.create_user(username='author', password='password')


@pytest.fixture
def other_user():
    """Фикстура для создания другого пользователя."""
    return User.objects.create_user(username='other_user', password='password')


@pytest.fixture
def news():
    """Фикстура для создания тестовой новости."""
    return News.objects.create(
        title='Тестовая новость',
        text='Это текст тестовой новости.',
        date='2023-10-01'
    )


@pytest.fixture
def comment(author, news):
    """Фикстура для создания тестового комментария."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Это тестовый комментарий.'
    )


@pytest.fixture
def multiple_news():
    """Фикстура для создания нескольких новостей."""
    return News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=f'2023-10-{index + 1:02d}'  # Даты от 2023-10-01 до 2023-10-05
        )
        for index in range(15)
    )


@pytest.fixture
def multiple_comments(author, news):
    """Фикстура для создания нескольких комментариев."""
    now = datetime.now()
    comments = [
        Comment(
            news=news,
            author=author,
            text=f'Комментарий {index}',
            created=now - timedelta(days=index)
        )
        for index in range(5)
    ]
    return Comment.objects.bulk_create(comments)


@pytest.fixture
def detail_url(news):
    """Фикстура для создания URL страницы деталей новости."""
    return reverse('news:detail', kwargs={'pk': news.pk})


@pytest.fixture
def edit_url(comment):
    """Фикстура для создания URL редактирования комментария."""
    return reverse('news:edit', kwargs={'pk': comment.pk})


@pytest.fixture
def delete_url(comment):
    """Фикстура для создания URL удаления комментария."""
    return reverse('news:delete', kwargs={'pk': comment.pk})


@pytest.fixture
def authenticated_client(client, author):
    """Фикстура для авторизованного клиента."""
    client.force_login(author)
    return client


@pytest.fixture
def home_url():
    """Фикстура для URL главной страницы."""
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    """Фикстура для URL страницы новости."""
    return reverse('news:detail', kwargs={'pk': news.pk})


@pytest.fixture
def comment_edit_url(comment):
    """Фикстура для URL страницы редактирования комментария."""
    return reverse('news:edit', kwargs={'pk': comment.pk})


@pytest.fixture
def comment_delete_url(comment):
    """Фикстура для URL страницы удаления комментария."""
    return reverse('news:delete', kwargs={'pk': comment.pk})


@pytest.fixture
def login_url():
    """Фикстура для URL страницы входа."""
    return reverse('users:login')


@pytest.fixture
def logout_url():
    """Фикстура для URL страницы выхода."""
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    """Фикстура для URL страницы регистрации."""
    return reverse('users:signup')
