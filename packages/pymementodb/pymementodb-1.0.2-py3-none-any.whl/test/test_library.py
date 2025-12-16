from unittest import TestCase
from datetime import datetime, timezone
from pymementodb import Library


class TestLibrary(TestCase):

    def test_init(self):
        data = {
          "id": "ht5dj7hqtey87",
          "name": "Library1",
          "owner": "author",
          "createdTime": "2015-08-05T08:40:51.620Z",
          "modifiedTime": "2016-08-05T08:40:51.620Z",
          "size": 2353,
          "revision": 10,
          "fields": [{'id': 1, 'type': 'datetime', 'name': 'Date', 'order': 0, 'options': None, 'role': 'desc'},
                     {'id': 2, 'type': 'text', 'name': 'From', 'order': 1, 'options': None, 'role': None}]
        }
        lib = Library(**data)
        self.assertEqual(lib.id, 'ht5dj7hqtey87')
        self.assertEqual(lib.name, 'Library1')
        self.assertEqual(lib.owner, 'author')
        self.assertEqual(lib.createdTime,
                         datetime(2015, 8, 5, 8, 40, 51, 620000, tzinfo=timezone.utc))
        self.assertEqual(lib.modifiedTime,
                         datetime(2016, 8, 5, 8, 40, 51, 620000, tzinfo=timezone.utc))
