from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from notes.forms import NoteForm
from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class LogicTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем тестового пользователя (владельца заметки)
        cls.owner = User.objects.create_user(
            username='owner',
            password='testpassword123'
        )
        # Создаем второго пользователя (постороннего)
        cls.other_user = User.objects.create_user(
            username='other_user',
            password='testpassword123'
        )
        # Данные для создания заметки
        cls.note_data = {
            'title': 'Тестовая заметка',
            'text': 'Текст заметки',
            'slug': 'test-note',
        }
        # Создаем заметку от имени владельца
        cls.note = Note.objects.create(
            title='Заметка владельца',
            text='Текст заметки.',
            slug='owner-note',
            author=cls.owner
        )

    def setUp(self):
        # Создаем экземпляр клиента
        self.client = Client()

    def test_authenticated_user_can_create_note(self):
        # Авторизуем пользователя
        self.client.force_login(self.owner)
        # Получаем URL для страницы создания заметки
        url = reverse('notes:add')
        # Выполняем POST-запрос для создания заметки
        response = self.client.post(url, data=self.note_data)
        # Проверяем, что заметка была создана
        self.assertEqual(Note.objects.count(), 2)
        # Проверяем, что пользователь перенаправлен на страницу успешного
        # добавления
        self.assertRedirects(response, reverse('notes:success'))

    def test_anonymous_user_cannot_create_note(self):
        # Получаем URL для страницы создания заметки
        url = reverse('notes:add')
        # Выполняем POST-запрос для создания заметки
        response = self.client.post(url, data=self.note_data)
        # Проверяем, что заметка не была создана
        self.assertEqual(Note.objects.count(), 1)
        # Проверяем, анонимный пользователь перенаправлен на страницу логина
        self.assertRedirects(response, f"{reverse('users:login')}?next={url}")

    def test_duplicate_slug_not_allowed(self):
        # Пытаемся создать вторую заметку с тем же slug
        duplicate_note_data = {
            'title': 'Другая заметка',
            'text': 'Текст другой заметки.',
            'slug': 'owner-note',
        }
        # Создаем форму и передаем автора
        form = NoteForm(
            data=duplicate_note_data, initial={'author': self.owner}
        )
        # Проверяем, что форма не валидна
        self.assertFalse(form.is_valid())
        # Проверяем, что в ошибках формы есть ошибка для поля slug
        self.assertTrue('slug' in form.errors)
        # Проверяем полный текст ошибки
        expected_error = (
            'owner-note - такой slug уже существует, '
            'придумайте уникальное значение!'
        )
        self.assertIn(expected_error, form.errors['slug'])
        # Проверяем, что количество заметок в базе данных не изменилось
        self.assertEqual(Note.objects.count(), 1)

    def test_auto_generate_slug(self):
        # Данные для создания заметки без указания slug
        form_data = {
            'title': 'Тестовая заметка с автоматическим slug',
            'text': 'Текст заметки.',
            # Поле slug не заполнено
        }
        # Создаем форму и передаем автора
        form = NoteForm(data=form_data, initial={'author': self.owner})
        # Проверяем, что форма валидна
        self.assertTrue(form.is_valid())
        # Сохраняем заметку
        note = form.save(commit=False)
        note.author = self.owner
        note.save()
        # Проверяем, что slug сгенерирован корректно
        expected_slug = slugify(form_data['title'])[:100]
        self.assertEqual(note.slug, expected_slug)

    def test_owner_can_edit_note(self):
        # Владелец может редактировать свою заметку
        self.client.force_login(self.owner)
        url = reverse('notes:edit', args=[self.note.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Доступ разрешен

    def test_other_user_cannot_edit_note(self):
        # Посторонний пользователь не может редактировать чужую заметку
        self.client.force_login(self.other_user)
        url = reverse('notes:edit', args=[self.note.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_owner_can_delete_note(self):
        # Владелец может удалить свою заметку
        self.client.force_login(self.owner)
        url = reverse('notes:delete', args=[self.note.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_delete_note(self):
        # Посторонний пользователь не может удалить чужую заметку
        self.client.force_login(self.other_user)
        url = reverse('notes:delete', args=[self.note.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
