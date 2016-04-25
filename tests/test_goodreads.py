import datetime
import unittest
from unittest import mock

from rattle_cli.goodreads import Goodreads


class TestUser(unittest.TestCase):

    user_id = "1234"
    user_name = "Test User"

    user_xml = """<?xml version="1.0" encoding="UTF-8"?>
<GoodreadsResponse>
  <Request />
  <user id="%(user_id)s">
    <name>%(user_name)s</name>
  </user>
</GoodreadsResponse>
"""

    def setUp(self):
        session = mock.Mock()
        self.goodreads = Goodreads(session)

    def test_initialise_user(self):
        self.assertEqual(self.goodreads.user_id, None)

        xml = self.user_xml % {'user_id': self.user_id,
                               'user_name': self.user_name}
        response = mock.Mock()
        response.content = xml

        self.goodreads.session.get.return_value = response
        self.goodreads.initialise_user()
        self.assertEqual(self.goodreads.user_id, self.user_id)

    def test_initialise_no_user_id(self):
        self.assertEqual(self.goodreads.user_id, None)

        response = mock.Mock()
        response.content = """<?xml version="1.0" encoding="UTF-8"?>
<GoodreadsResponse>
  <Request />
  <user><name>User Name</name></user>
</GoodreadsResponse>
"""
        self.goodreads.session.get.return_value = response
        with self.assertRaises(SystemExit):
            self.goodreads.initialise_user()

    def test_authenticate_user_cant_parse(self):
        self.assertEqual(self.goodreads.user_id, None)

        response = mock.Mock()
        response.content = ""

        self.goodreads.session.get.return_value = response
        with self.assertRaises(SystemExit):
            self.goodreads.get_authenticated_user()


class TestReviewParsing(unittest.TestCase):

    def setUp(self):
        session = mock.Mock()
        self.goodreads = Goodreads(session)
        self.review = {'id': 1}

    def test_parse_date_read(self):
        self.review['read_at'] = "Fri Mar 04 00:00:00 -0800 2016"

        result = self.goodreads.parse_date_read(self.review)
        self.assertIsInstance(result, datetime.datetime)
        self.assertEqual(result.year, 2016)
        self.assertEqual(result.month, 3)
        self.assertEqual(result.day, 4)

    def test_parse_date_read_cant_parse(self):
        bad_date = "This is not a date"
        self.review['read_at'] = bad_date

        result = self.goodreads.parse_date_read(self.review)
        self.assertIsInstance(result, str)
        self.assertEqual(result, bad_date)

    def test_parse_date_read_empty(self):
        self.review['read_at'] = ""

        result = self.goodreads.parse_date_read(self.review)
        self.assertIsInstance(result, str)
        self.assertEqual(result, "")

    def test_parse_date_no_date(self):
        result = self.goodreads.parse_date_read(self.review)
        self.assertEqual(result, "")
