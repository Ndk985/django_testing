import pytest
from django.urls import reverse
from news.models import Comment
from http import HTTPStatus
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cannot_post_comment(client, detail_url):
    comment_data = {
        'text': 'Это тестовый комментарий от анонимного пользователя.'
    }
    response = client.post(detail_url, data=comment_data)

    assert response.status_code == HTTPStatus.FOUND, (
        'Анонимный пользователь должен быть перенаправлен'
        ' на страницу авторизации.'
    )
    assert Comment.objects.count() == 0, (
        'Анонимный пользователь не должен иметь возможности'
        ' создавать комментарии.'
    )


@pytest.mark.django_db
def test_authenticated_user_can_post_comment(
    authenticated_client, detail_url, author, news
):
    comment_data = {
        'text': 'Это тестовый комментарий от авторизованного пользователя.'
    }
    response = authenticated_client.post(detail_url, data=comment_data)

    assert response.status_code == HTTPStatus.FOUND, (
        'После успешной отправки комментария пользователь'
        ' должен быть перенаправлен.'
    )
    assert Comment.objects.count() == 1, (
        'Комментарий должен быть создан в базе данных.'
    )

    comment = Comment.objects.first()
    assert comment.text == comment_data['text'], (
        'Текст комментария должен совпадать с отправленным.'
    )
    assert comment.author == author, (
        'Автор комментария должен совпадать с авторизованным пользователем.'
    )
    assert comment.news == news, (
        'Комментарий должен быть связан с правильной новостью.'
    )


@pytest.mark.django_db
@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_with_bad_words_is_rejected(
    authenticated_client, detail_url, bad_word
):
    comment_data = {'text': f'Комментарий с запрещённым словом {bad_word}.'}
    response = authenticated_client.post(detail_url, data=comment_data)

    assert response.status_code == HTTPStatus.OK, (
        'Форма должна вернуть ошибку, а не перенаправлять пользователя.'
    )
    assert Comment.objects.count() == 0, (
        'Комментарий с запрещёнными словами не должен быть создан.'
    )
    assert 'form' in response.context, (
        'Форма должна быть возвращена в контексте для отображения ошибки.'
    )
    assert 'text' in response.context['form'].errors, (
        'Форма должна содержать ошибку в поле "text".'
    )
    assert 'Не ругайтесь!' in response.context['form'].errors['text'], (
        f'Форма должна вернуть ошибку "{WARNING}".'
    )


@pytest.mark.django_db
def test_authenticated_user_can_edit_own_comment(
    authenticated_client, edit_url, comment, news
):
    updated_comment_data = {'text': 'Это обновлённый комментарий.'}
    response = authenticated_client.post(edit_url, data=updated_comment_data)

    assert response.status_code == HTTPStatus.FOUND, (
        'После успешного редактирования комментария пользователь'
        ' должен быть перенаправлен.'
    )
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == updated_comment_data['text'], (
        'Текст комментария должен быть обновлён.'
    )
    assert response.url == reverse(
        'news:detail', kwargs={'pk': news.pk}) + '#comments', (
        'Перенаправление должно вести на страницу новости с якорем #comments.'
    )


@pytest.mark.django_db
def test_authenticated_user_can_delete_own_comment(
    authenticated_client, delete_url, comment, news
):
    response = authenticated_client.post(delete_url)

    assert response.status_code == HTTPStatus.FOUND, (
        'После успешного удаления комментария пользователь'
        ' должен быть перенаправлен.'
    )
    assert not Comment.objects.filter(pk=comment.pk).exists(), (
        'Комментарий должен быть удалён из базы данных.'
    )
    assert response.url == reverse(
        'news:detail', kwargs={'pk': news.pk}) + '#comments', (
        'Перенаправление должно вести на страницу новости с якорем #comments.'
    )


@pytest.mark.django_db
def test_authenticated_user_cannot_edit_other_users_comment(
    client, other_user, edit_url
):
    client.force_login(other_user)
    updated_comment_data = {
        'text': 'Это попытка редактирования чужого комментария.'
    }
    response = client.post(edit_url, data=updated_comment_data)

    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'Пользователь не должен иметь доступ'
        ' к редактированию чужих комментариев.'
    )


@pytest.mark.django_db
def test_authenticated_user_cannot_delete_other_users_comment(
    client, other_user, delete_url
):
    client.force_login(other_user)
    response = client.post(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'Пользователь не должен иметь доступ к удалению чужих комментариев.'
    )
