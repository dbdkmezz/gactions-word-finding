from unittest.mock import Mock, patch

from django.test import TestCase
from django.http import HttpResponse

from libs.google_actions.tests.mocks import MockRequest

from apps.word_finding.views import index


class TestViews(TestCase):
    def test_hello_world_if_not_json(self):
        result = index(MockRequest(body='NOT JSON'))
        self.assertIsInstance(result, HttpResponse)
        self.assertIn("Hello world", str(result.content))

    @patch('apps.word_finding.views.JsonResponse')
    @patch('apps.word_finding.views.AppRequest')
    @patch('apps.word_finding.views.User.objects.get_or_create')
    @patch('apps.word_finding.views.AppResponse')
    def test_welcome_if_new_user(
            self,
            mock_app_response,
            mock_get_or_create_user,
            *args
    ):
        mock_user = Mock()
        mock_user.get_next_question.return_value = "What's a pea?"
        mock_get_or_create_user.return_value = (mock_user, True)

        index(None)
        ask_string = mock_app_response().ask.call_args[0][0]

        self.assertEqual(mock_app_response().ask.call_count, 1)
        self.assertIn('Welcome to word finding practice. ', ask_string)
        self.assertIn(" What's a pea?", ask_string)
