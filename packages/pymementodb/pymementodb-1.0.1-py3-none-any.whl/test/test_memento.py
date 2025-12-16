from unittest import TestCase
import logging
import os
import random
from typing import List
from datetime import datetime
from pymementodb import Memento, Entry, MementoUnauthorizedException


class TestTemplate(TestCase):

    @staticmethod
    def get_auth_tokens() -> List[str]:
        try:
            return os.environ['MEMENTO_AUTH_TOKENS'].split(',')
        except KeyError:
            message = 'MEMENTO_AUTH_TOKENS environment variable is not set. Cannot run tests. ' \
                      'Tokens to be found in Desktop/Mac Memento apps. ' \
                      'Delimit them by comma, value example: ' \
                      'mNV9fylnhqTqY9QwQMDE5OWf7C9TpX,KJIleEPKN3PoKPBrYIJkEwroCphRz3'
            raise EnvironmentError(message)

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)
        cls.auth_tokens = cls.get_auth_tokens()

    def setUp(self) -> None:
        self.server = Memento(self.auth_tokens[0])
        for auth_token in self.auth_tokens[1:-1]:
            self.server.add_auth_token(auth_token)
        self.test_lib_id = None
        for lib_info in self.server.list_libraries():
            if lib_info['name'] == 'PyMemento Test':
                self.test_lib_id = lib_info['id']
                break
        else:
            raise EnvironmentError('Did not find "PyMemento Test" library on the server.')
        self.purge_library(self.test_lib_id)

        self.test_linked_lib_id = None
        for lib_info in self.server.list_libraries():
            if lib_info['name'] == 'PyMemento Linked Test':
                self.test_linked_lib_id = lib_info['id']
                break
        else:
            raise EnvironmentError('Did not find "PyMemento Linked Test" library on the server.')
        self.purge_library(self.test_linked_lib_id)

    def tearDown(self) -> None:
        self.purge_library(self.test_lib_id)

    def create_random_entries(self, num_entries: int,
                              test_lib_id: str, test_linked_lib_id: str = None) -> List[Entry]:
        new_entries = []
        field_specifications = self.server.get_library(test_lib_id).fields
        linked_lib_entries = []
        if test_linked_lib_id is not None:
            linked_lib_entries = [entry for entry in self.create_random_entries(5, test_linked_lib_id)]
        for _ in range(num_entries):
            field_values = []
            for field in field_specifications:
                if field.type == 'text':
                    value = 'Text'
                elif field.type == 'richtext':
                    value = 'Text'
                elif field.type == 'int':
                    value = random.randrange(-100, 100)
                elif field.type == 'double':
                    value = random.uniform(-100, 100)
                    value = round(value, 2)
                elif field.type == 'boolean':
                    value = random.choice([True, False])
                elif field.type == 'datetime':
                    value = '2023-08-31T16:47:00+00:00'
                elif field.type == 'time':
                    value = '12:14:00Z'
                elif field.type == 'entries':
                    num_linked_entries = random.randrange(0, len(linked_lib_entries))
                    random_linked_entries = random.sample(linked_lib_entries, k=num_linked_entries)
                    value = [entry.id for entry in random_linked_entries]
                else:
                    raise NotImplementedError(f'Random value generation for field '
                                              f'of the type {field.type} is not implemented.')
                field_values.append({'id': field.id,
                                     'value': value})
            new_entry = self.server.create_entry(test_lib_id, field_values)
            new_entries.append(new_entry)

        return new_entries

    def purge_library(self, lib_id: str) -> None:
        for entry in self.server.get_entries(lib_id):
            if entry.status != 'deleted':
                self.server.delete_entry(lib_id, entry.id)


class TestMemento(TestTemplate):

    def test_unauthorized(self):
        server = Memento('12345')
        self.assertRaises(MementoUnauthorizedException, server.list_libraries)

    def test_get_libraries(self):
        lib_infos = self.server.list_libraries()
        test_lib_info = None
        for lib_info in lib_infos:
            if lib_info['id'] == self.test_lib_id:
                test_lib_info = lib_info
                break
        self.assertEqual(test_lib_info['id'], self.test_lib_id)
        self.assertEqual(test_lib_info['name'], 'PyMemento Test')
        self.assertTrue(test_lib_info['owner'])
        self.assertIs(type(test_lib_info['createdTime']), datetime)

    def test_get_library(self):
        lib = self.server.get_library(self.test_lib_id)
        self.assertEqual(lib.id, self.test_lib_id)
        self.assertEqual(lib.name, 'PyMemento Test')
        self.assertTrue(lib.owner)
        self.assertIs(type(lib.createdTime), datetime)

    def test_get_entries(self):
        new_entries = self.create_random_entries(1, self.test_lib_id, self.test_linked_lib_id)
        entries = self.server.get_entries(self.test_lib_id)
        new_entry = new_entries[0]
        entry = entries[-1]
        self.assertEqual(entry.id, new_entry.id)
        self.assertEqual(entry.author, new_entry.author)
        self.assertEqual(entry.revision, new_entry.revision)
        self.assertEqual(entry.status, new_entry.status)
        self.assertEqual(entry.size, new_entry.size)
        self.assertEqual(entry.createdTime, new_entry.createdTime)
        self.assertEqual(entry.modifiedTime, new_entry.modifiedTime)
        self.assertEqual(len(entry.fields), len(new_entry.fields))

    def test_get_entries_limit(self):
        self.create_random_entries(10, self.test_lib_id, self.test_linked_lib_id)
        entries = self.server.get_entries(self.test_lib_id, limit=5)
        self.assertEqual(len(entries), 5)

    def test_get_entries_field_ids(self):
        self.create_random_entries(2, self.test_lib_id, self.test_linked_lib_id)
        entries = self.server.get_entries(self.test_lib_id, field_ids=[0, 2])
        self.assertEqual(len(entries[-1].fields), 2)

    def test_get_entries_start_revision(self):
        self.create_random_entries(2, self.test_lib_id, self.test_linked_lib_id)
        entries = self.server.get_entries(self.test_lib_id, start_revision=1)
        self.assertGreater(len(entries), 0)
        self.assertTrue(all(entry.revision >= 1 for entry in entries))

    def test_get_entry(self):
        field_values = [{'id': 0, 'value': 'Text'},
                        {'id': 1, 'value': -77},
                        {'id': 2, 'value': -49.75},
                        {'id': 3, 'value': False},
                        {'id': 4, 'value': '2023-08-31T16:47:00+00:00'},
                        {'id': 5, 'value': '12:14:00Z'}]
        new_entry = self.server.create_entry(self.test_lib_id, field_values)
        entry = self.server.get_entry(self.test_lib_id, new_entry.id)
        self.assertEqual(entry.id, new_entry.id)
        self.assertEqual(entry.author, new_entry.author)
        self.assertEqual(entry.revision, new_entry.revision)
        self.assertEqual(entry.status, new_entry.status)
        self.assertEqual(entry.size, new_entry.size)
        self.assertEqual(entry.createdTime, new_entry.createdTime)
        self.assertEqual(entry.modifiedTime, new_entry.modifiedTime)
        self.assertListEqual(entry.fields, new_entry.fields)

    def test_edit_entry(self):
        field_values = [{'id': 0, 'value': 'Text'},
                        {'id': 1, 'value': -77},
                        {'id': 2, 'value': -49.75},
                        {'id': 3, 'value': False},
                        {'id': 4, 'value': '2023-08-31T16:47:00+00:00'},
                        {'id': 5, 'value': '12:14:00Z'}]
        entry = self.server.create_entry(self.test_lib_id, field_values)
        entry = self.server.edit_entry(self.test_lib_id, entry.id, [{'id': 0, 'value': 'New value'}])
        new_fields = {'id': 0, 'name': 'Text', 'type': 'text', 'value': 'New value'}
        self.assertIn(new_fields, entry.fields)

    def test_create_entry(self):
        field_values = [{'id': 0, 'value': 'Text'},
                        {'id': 1, 'value': -77},
                        {'id': 2, 'value': -49.75},
                        {'id': 3, 'value': False},
                        {'id': 4, 'value': '2023-08-31T16:47:00+00:00'},
                        {'id': 5, 'value': '12:14:00Z'}]
        entry = self.server.create_entry(self.test_lib_id, field_values)
        self.assertEqual(len(entry.fields), 6)

    def test_delete_entry(self):
        field_values = [{'id': 0, 'value': 'Text'},
                        {'id': 1, 'value': -77},
                        {'id': 2, 'value': -49.75},
                        {'id': 3, 'value': False},
                        {'id': 4, 'value': '2023-08-31T16:47:00+00:00'},
                        {'id': 5, 'value': '12:14:00Z'}]
        entry = self.server.create_entry(self.test_lib_id, field_values)
        self.server.delete_entry(self.test_lib_id, entry.id)
        entry = self.server.get_entry(self.test_lib_id, entry.id)
        self.assertEqual('deleted', entry.status)
