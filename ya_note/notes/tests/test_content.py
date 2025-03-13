from .base_tests import BaseTest
from notes.forms import NoteForm


class ContentTests(BaseTest):
    def test_note_in_object_list(self):
        response = self.author_client.get(self.LIST_URL)
        self.assertIn(self.note, response.context['object_list'])

    def test_user_sees_only_own_notes(self):
        response = self.author_client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        self.assertNotIn(self.other_note, object_list)
        self.assertEqual(len(object_list), 1)

    def test_forms_passed_to_create_and_edit_pages(self):
        create_response = self.author_client.get(self.ADD_URL)
        self.assertIn('form', create_response.context)
        self.assertIsInstance(create_response.context['form'], NoteForm)

        edit_response = self.author_client.get(self.EDIT_URL)
        self.assertIn('form', edit_response.context)
        self.assertIsInstance(edit_response.context['form'], NoteForm)
