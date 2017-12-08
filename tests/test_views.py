from django.test import TestCase
from django.http import HttpResponse

from libs.google_actions.tests.mocks import MockRequest

from apps.word_finding.views import index


class TestViews(TestCase):
    def test_hello_world_if_not_json(self):
        result = index(MockRequest(body='NOT JSON'))
        self.assertIs(type(result), HttpResponse)
        self.assertIn("Hello world", str(result.content))
