import pytest
from http import HTTPStatus


@pytest.mark.django_db
def test_all_pages_access(
    client,
    author,
    other_user,
    news,
    comment,
    home_url,
    news_detail_url,
    comment_edit_url,
    comment_delete_url,
    signup_url,
    login_url,
    logout_url
):
    cases = [
        # Главная страница доступна анонимному пользователю.
        [home_url, None, HTTPStatus.OK],

        # Страница отдельной новости доступна анонимному пользователю.
        [news_detail_url, None, HTTPStatus.OK],

        # Страницы удаления и редактирования комментария доступны автору
        # комментария.
        [comment_edit_url, author, HTTPStatus.OK],
        [comment_delete_url, author, HTTPStatus.OK],

        # При попытке перейти на страницу редактирования или удаления
        # комментария анонимный пользователь перенаправляется на страницу
        # авторизации.
        [comment_edit_url, None, HTTPStatus.FOUND],
        [comment_delete_url, None, HTTPStatus.FOUND],

        # Авторизованный пользователь не может зайти на страницы редактирования
        # или удаления чужих комментариев (возвращается ошибка 404).
        [comment_edit_url, other_user, HTTPStatus.NOT_FOUND],
        [comment_delete_url, other_user, HTTPStatus.NOT_FOUND],

        # Страницы регистрации пользователей, входа в учётную запись и выхода
        # из неё доступны анонимным пользователям.
        [signup_url, None, HTTPStatus.OK],
        [login_url, None, HTTPStatus.OK],
        [logout_url, None, HTTPStatus.OK],
    ]

    for url, user, expected_status in cases:
        # Очищаем сессию перед каждым тестом
        client.session.flush()

        # Логинимся если есть пользователь
        if user:
            client.force_login(user)

        response = client.get(url)
        assert response.status_code == expected_status

        # Дополнительные проверки для редиректов
        if expected_status == HTTPStatus.FOUND:
            assert response.url.startswith(login_url)
