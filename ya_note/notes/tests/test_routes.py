from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class RoutesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем тестовых пользователей
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        cls.author = User.objects.create_user(
            username='author',
            password='authorpassword123'
        )
        cls.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpassword123'
        )
        # Создаем тестовую заметку
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-note',
            author=cls.author,
        )

    def setUp(self):
        # Создаем экземпляр клиента
        self.client = Client()

    def test_home_page_accessible_to_anonymous_user(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_access(self):
        # Авторизуем пользователя
        self.client.force_login(self.user)
        urls = [
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:add'),
        ]
        # Проверяем доступность каждой страницы
        self._test_urls_access(urls, 200)

    def test_author_access_to_note_pages(self):
        # Авторизуем автора заметки
        self.client.force_login(self.author)
        urls = [
            reverse('notes:detail', args=[self.note.slug]),
            reverse('notes:edit', args=[self.note.slug]),
            reverse('notes:delete', args=[self.note.slug]),
        ]
        # Проверяем доступность каждой страницы для автора
        self._test_urls_access(urls, 200)

    def test_other_user_access_to_note_pages(self):
        # Авторизуем другого пользователя
        self.client.force_login(self.other_user)
        urls = [
            reverse('notes:detail', args=[self.note.slug]),
            reverse('notes:edit', args=[self.note.slug]),
            reverse('notes:delete', args=[self.note.slug]),
        ]
        # Проверяем, что другой пользователь получает 404
        self._test_urls_access(urls, 404)

    def test_anonymous_user_redirected_to_login(self):
        urls = [
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:add'),
            reverse('notes:detail', args=[self.note.slug]),
            reverse('notes:edit', args=[self.note.slug]),
            reverse('notes:delete', args=[self.note.slug]),
        ]
        # Проверяем, анонимный пользователь перенаправляется на страницу логина
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertRedirects(
                    response, f"{reverse('users:login')}?next={url}"
                )

    def test_auth_pages_accessible_to_all_users(self):
        urls = [
            reverse('users:login'),
            reverse('users:logout'),
            reverse('users:signup'),
        ]
        # Проверяем доступность каждой страницы для анонимного пользователя
        self._test_urls_access(urls, 200)
        # Авторизуем пользователя
        self.client.force_login(self.user)
        # Проверяем доступность каждой страницы для аутентифицированного
        # пользователя
        self._test_urls_access(urls, 200)

    def _test_urls_access(self, urls, expected_status_code):
        """Вспомогательный метод проверки доступности списка URL-адресов."""
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    expected_status_code,
                    f"Страница {url} вернула статус {response.status_code},\
                      ожидалось {expected_status_code}"
                )
