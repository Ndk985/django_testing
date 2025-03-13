from .base_tests import BaseTest
from http import HTTPStatus


class RoutesTests(BaseTest):
    def test_url_access(self):
        """Проверка доступности URL для разных клиентов."""
        cases = [
            # Анонимный пользователь
            [self.HOME_URL, self.anonymous_client, HTTPStatus.OK],
            [self.LIST_URL, self.anonymous_client, HTTPStatus.FOUND],
            [self.SUCCESS_URL, self.anonymous_client, HTTPStatus.FOUND],
            [self.ADD_URL, self.anonymous_client, HTTPStatus.FOUND],
            [self.DETAIL_URL, self.anonymous_client, HTTPStatus.FOUND],
            [self.EDIT_URL, self.anonymous_client, HTTPStatus.FOUND],
            [self.DELETE_URL, self.anonymous_client, HTTPStatus.FOUND],
            [self.LOGIN_URL, self.anonymous_client, HTTPStatus.OK],
            [self.LOGOUT_URL, self.anonymous_client, HTTPStatus.OK],
            [self.SIGNUP_URL, self.anonymous_client, HTTPStatus.OK],

            # Аутентифицированный пользователь (автор)
            [self.LIST_URL, self.author_client, HTTPStatus.OK],
            [self.SUCCESS_URL, self.author_client, HTTPStatus.OK],
            [self.ADD_URL, self.author_client, HTTPStatus.OK],
            [self.DETAIL_URL, self.author_client, HTTPStatus.OK],
            [self.EDIT_URL, self.author_client, HTTPStatus.OK],
            [self.DELETE_URL, self.author_client, HTTPStatus.OK],
            [self.LOGIN_URL, self.author_client, HTTPStatus.OK],
            [self.LOGOUT_URL, self.author_client, HTTPStatus.OK],
            [self.SIGNUP_URL, self.author_client, HTTPStatus.OK],

            # Другой пользователь (не автор)
            [self.DETAIL_URL, self.other_client, HTTPStatus.NOT_FOUND],
            [self.EDIT_URL, self.other_client, HTTPStatus.NOT_FOUND],
            [self.DELETE_URL, self.other_client, HTTPStatus.NOT_FOUND],
        ]

        for url, client, expected_status in cases:
            with self.subTest(
                url=url, client=client, expected_status=expected_status
            ):
                response = client.get(url)
                self.assertEqual(
                    response.status_code,
                    expected_status,
                    f"Страница {url} вернула статус {response.status_code}, "
                    f"ожидалось {expected_status}"
                )

    def test_anonymous_user_redirected_to_login(self):
        """Анонимный пользователь перенаправляется на страницу входа."""
        urls = [
            self.LIST_URL,
            self.SUCCESS_URL,
            self.ADD_URL,
            self.DETAIL_URL,
            self.EDIT_URL,
            self.DELETE_URL,
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.anonymous_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response, f"{self.LOGIN_URL}?next={url}")
