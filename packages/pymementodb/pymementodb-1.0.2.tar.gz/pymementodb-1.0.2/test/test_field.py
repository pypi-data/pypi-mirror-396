from unittest import TestCase
from pymementodb.field import Field


class TestField(TestCase):

    def test_init(self):
        data = {
          'id': 1,
          'lib_id': '12345',
          'name': 'Title',
          'order': 0,
          'role': 'name',
          'type': 'text'
        }
        field = Field(**data)
        self.assertEqual(field.id, 1)
        self.assertEqual(field.name, 'Title')
        self.assertEqual(field.order, 0)
        self.assertEqual(field.role, 'name')
        self.assertEqual(field.type, 'text')
