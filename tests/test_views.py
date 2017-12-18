import pytest

from django.test import TestCase
from django.http import HttpResponse

from libs.google_actions.tests.mocks import MockRequest
from libs.google_actions.tests.utils import Utils as GoogleTestUtils

from apps.word_finding.views import index

from .factories import QuestionFactory


@pytest.mark.django_db
class TestViews(TestCase):
    def test_hello_world_if_not_json(self):
        result = index(MockRequest(body='NOT JSON'))
        self.assertIsInstance(result, HttpResponse)
        self.assertIn("Hello world", str(result.content))

    def test_welcome_if_new_user(self):
        QuestionFactory(question="What's a pea?")
        response = index(MockRequest())
        response_text = GoogleTestUtils.get_text_from_google_response(response)
        self.assertIn('Welcome to word finding practice. ', response_text)
        self.assertIn(" What's a pea?", response_text)
