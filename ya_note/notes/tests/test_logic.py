from .base_tests import BaseTest
from notes.forms import NoteForm
from notes.models import Note
from pytils.translit import slugify
from http import HTTPStatus


class LogicTests(BaseTest):
    def test_authenticated_user_can_create_note(self):
        initial_count = Note.objects.count()
        note_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'new-note',
        }
        response = self.author_client.post(self.ADD_URL, data=note_data)
        self.assertEqual(Note.objects.count(), initial_count + 1)
        self.assertRedirects(response, self.SUCCESS_URL)

    def test_anonymous_user_cannot_create_note(self):
        initial_count = Note.objects.count()
        response = self.anonymous_client.post(
            self.ADD_URL, data=self.note_data
        )
        self.assertEqual(Note.objects.count(), initial_count)
        self.assertRedirects(response, f"{self.LOGIN_URL}?next={self.ADD_URL}")

    def test_duplicate_slug_not_allowed(self):
        initial_count = Note.objects.count()
        duplicate_note_data = {
            'title': 'Другая заметка',
            'text': 'Текст другой заметки.',
            'slug': self.SLUG,
        }
        form = NoteForm(
            data=duplicate_note_data, initial={'author': self.author}
        )
        self.assertFalse(form.is_valid())
        self.assertTrue('slug' in form.errors)
        expected_error = (
            f"{self.SLUG} - такой slug уже существует, "
            "придумайте уникальное значение!"
        )
        self.assertIn(expected_error, form.errors['slug'])
        self.assertEqual(Note.objects.count(), initial_count)

    def test_auto_generate_slug(self):
        form_data = {
            'title': 'Тестовая заметка с автоматическим slug',
            'text': 'Текст заметки.',
        }
        form = NoteForm(data=form_data, initial={'author': self.author})
        self.assertTrue(form.is_valid())
        note = form.save(commit=False)
        note.author = self.author
        note.save()
        expected_slug = slugify(form_data['title'])[:100]
        self.assertEqual(note.slug, expected_slug)

    def test_owner_can_edit_note(self):
        response = self.author_client.get(self.EDIT_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form', response.context)
        form = response.context['form']
        note = Note.objects.get(pk=self.note.pk)
        # Проверяем, значения всех полей в форме соответствуют данным из базы
        self.assertEqual(form.initial['title'], note.title)
        self.assertEqual(form.initial['text'], note.text)
        self.assertEqual(form.initial['slug'], note.slug)

    def test_other_user_cannot_edit_note(self):
        response = self.other_client.get(self.EDIT_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        updated_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(updated_note.title, self.note.title)
        self.assertEqual(updated_note.text, self.note.text)
        self.assertEqual(updated_note.slug, self.note.slug)
        self.assertEqual(updated_note.author, self.note.author)

    def test_owner_can_delete_note(self):
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
        response = self.author_client.get(self.DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        delete_response = self.author_client.post(self.DELETE_URL)
        self.assertEqual(delete_response.status_code, HTTPStatus.FOUND)
        # Проверяем, что заметка удалена из базы данных
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())
        self.assertEqual(delete_response.url, self.SUCCESS_URL)

    def test_other_user_cannot_delete_note(self):
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
        response = self.other_client.get(self.DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Проверяем, что заметка всё ещё существует в базе данных
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
