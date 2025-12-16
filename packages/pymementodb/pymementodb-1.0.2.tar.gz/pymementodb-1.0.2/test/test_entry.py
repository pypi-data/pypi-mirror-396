from unittest import TestCase
from datetime import datetime, timezone
from pymementodb.entry import Entry


class TestField(TestCase):
    def setUp(self) -> None:
        self.test_data = {
          "id": "frejf944jfnjsdf4",
          "lib_id": "12345",
          "author": "author",
          "createdTime": "2015-08-05T08:40:51.620Z",
          "modifiedTime": "2016-08-05T08:40:51.620Z",
          "revision": 10,
          "status": "active",
          "size": 20,
          "fields": [
            {
              "id": 1,
              "value": "Record 1"
            },
            {
              "id": 2,
              "value": 1000
            }
          ]
        }

    def test_init(self):
        entry = Entry(**self.test_data)
        self.assertEqual(entry.id, 'frejf944jfnjsdf4')
        self.assertEqual(entry.author, 'author')
        self.assertEqual(entry.revision, 10)
        self.assertEqual(entry.status, 'active')
        self.assertEqual(entry.size, 20)
        self.assertEqual(entry.createdTime,
                         datetime(2015, 8, 5, 8, 40, 51, 620000, tzinfo=timezone.utc))
        self.assertEqual(entry.modifiedTime,
                         datetime(2016, 8, 5, 8, 40, 51, 620000, tzinfo=timezone.utc))

    def test_get_field_value(self):
        entry = Entry(**self.test_data)
        self.assertEqual(entry.get_field_value(1), 'Record 1')

    def test_get_field_value_missing(self):
        entry = Entry(**self.test_data)
        self.assertIsNone(entry.get_field_value(3))
