from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class ContentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем двух пользователей
        cls.author = User.objects.create_user(
            username='author',
            password='authorpassword123'
        )
        cls.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpassword123'
        )
        # Создаем заметку для первого пользователя
        cls.note = Note.objects.create(
            title='Тестовая заметка автора',
            text='Текст заметки автора',
            slug='test-note-author',
            author=cls.author,
        )
        # Создаем заметку для второго пользователя
        cls.other_note = Note.objects.create(
            title='Тестовая заметка другого пользователя',
            text='Текст заметки другого пользователя',
            slug='test-note-other',
            author=cls.other_user,
        )

    def setUp(self):
        # Создаем экземпляр клиента
        self.client = Client()
        # Авторизуем первого пользователя
        self.client.force_login(self.author)

    def test_note_in_object_list(self):
        # Получаем URL для страницы со списком заметок
        url = reverse('notes:list')
        # Выполняем GET-запрос
        response = self.client.get(url)
        # Проверяем, что заметка присутствует в object_list
        self.assertIn(self.note, response.context['object_list'])

    def test_user_sees_only_own_notes(self):
        # Получаем URL для страницы со списком заметок
        url = reverse('notes:list')
        # Выполняем GET-запрос
        response = self.client.get(url)
        # Проверяем, что в object_list только заметки авторизованного
        # пользователя
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        self.assertNotIn(self.other_note, object_list)
        # Проверяем, что в object_list только одна заметка
        self.assertEqual(len(object_list), 1)

    def test_forms_passed_to_create_and_edit_pages(self):
        # Проверяем страницу создания заметки
        create_url = reverse('notes:add')
        create_response = self.client.get(create_url)
        self.assertIn('form', create_response.context)
        self.assertIsInstance(create_response.context['form'], NoteForm)

        # Проверяем страницу редактирования заметки
        edit_url = reverse('notes:edit', args=[self.note.slug])
        edit_response = self.client.get(edit_url)
        self.assertIn('form', edit_response.context)
        self.assertIsInstance(edit_response.context['form'], NoteForm)
