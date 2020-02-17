from django.test import TestCase
from mixer.backend.django import mixer
import pytest
pytestmark = pytest.mark.django_db


class TestPeriod(TestCase):
    def test_model(self):
        obj = mixer.blend('search.Period')
        self.assertEqual(obj.pk, 1)

    def test_str(self):
        obj = mixer.blend('search.Period')
        self.assertEqual(str(obj), obj.period_text)


class TestItem(TestCase):
    def test_model(self):
        obj = mixer.blend('search.Item')
        self.assertEqual(obj.pk, 1)

    def test_str(self):
        obj = mixer.blend('search.Item')
        self.assertEqual(str(obj), obj.item_title)


class TestSubject(TestCase):
    def test_model(self):
        obj = mixer.blend('search.Subject')
        self.assertEqual(obj.pk, 1)

    def test_str(self):
        obj = mixer.blend('search.Subject')
        self.assertEqual(str(obj), obj.subject_url)


class TestAct(TestCase):
    def test_model(self):
        obj = mixer.blend('search.Act')
        self.assertEqual(obj.pk, 1)

    def test_str(self):
        obj = mixer.blend('search.Act')
        self.assertEqual(str(obj), obj.title)
