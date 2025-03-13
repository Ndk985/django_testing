from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class BaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Константы
        cls.USERNAME_AUTHOR = 'author'
        cls.USERNAME_OTHER_USER = 'otheruser'
        cls.PASSWORD = 'testpassword123'
        cls.SLUG = 'test-note'
        cls.SLUG_OTHER = 'test-note-other'
        cls.TITLE = 'Тестовая заметка'
        cls.TITLE_OTHER = 'Тестовая заметка другого пользователя'
        cls.TEXT = 'Текст заметки'
        cls.TEXT_OTHER = 'Текст заметки другого пользователя'

        # Пользователи
        cls.author = User.objects.create_user(
            username=cls.USERNAME_AUTHOR,
            password=cls.PASSWORD
        )
        cls.other_user = User.objects.create_user(
            username=cls.USERNAME_OTHER_USER,
            password=cls.PASSWORD
        )

        # Заметки
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author,
        )
        cls.other_note = Note.objects.create(
            title=cls.TITLE_OTHER,
            text=cls.TEXT_OTHER,
            slug=cls.SLUG_OTHER,
            author=cls.other_user,
        )

        # Данные для создания заметки
        cls.note_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG,
        }

        # Реверсы
        cls.HOME_URL = reverse('notes:home')
        cls.LIST_URL = reverse('notes:list')
        cls.SUCCESS_URL = reverse('notes:success')
        cls.ADD_URL = reverse('notes:add')
        cls.LOGIN_URL = reverse('users:login')
        cls.LOGOUT_URL = reverse('users:logout')
        cls.SIGNUP_URL = reverse('users:signup')

        # Динамические реверсы
        cls.DETAIL_URL = reverse('notes:detail', args=[cls.SLUG])
        cls.EDIT_URL = reverse('notes:edit', args=[cls.SLUG])
        cls.DELETE_URL = reverse('notes:delete', args=[cls.SLUG])

        # Клиенты
        cls.author_client = Client()
        cls.other_client = Client()
        cls.anonymous_client = Client()

        # Авторизация клиентов
        cls.author_client.force_login(cls.author)
        cls.other_client.force_login(cls.other_user)
