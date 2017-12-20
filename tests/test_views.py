import pytest

from django.test import TestCase
from django.http import HttpResponse

from libs.google_actions.tests.mocks import MockRequest
from libs.google_actions.tests.utils import Utils as GoogleTestUtils

from apps.word_finding.views import index
from apps.word_finding.models.user import User

from .factories import ExerciseFactory, QuestionFactory, UserFactory, ExerciseStateFactory


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

    def test_welcome_creates_user(self):
        QuestionFactory()
        self.assertEqual(User.objects.count(), 0)
        index(MockRequest())
        self.assertEqual(User.objects.count(), 1)

    def test_correct_answer(self):
        # TODO: remove second question from test when tests can complete
        user = UserFactory(user_id='user')
        exercise = ExerciseFactory()
        question = QuestionFactory(exercise=exercise, answer='right answer')
        QuestionFactory(exercise=exercise, question='puzzling question')
        ExerciseStateFactory(
            user=user,
            exercise=exercise,
            current_question=question,
            completed=False,
        )

        response = index(MockRequest(text='right answer', user_id='user'))
        response_text = GoogleTestUtils.get_text_from_google_response(response)

        self.assertIn("That's right! ", response_text)
        self.assertIn("puzzling question", response_text)
