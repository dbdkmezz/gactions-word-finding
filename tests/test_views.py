import pytest

from django.test import TestCase
from django.http import HttpResponse

from libs.google_actions.tests.mocks import MockRequest
from libs.google_actions.tests.utils import Utils as GoogleTestUtils

from apps.word_finding.views import index, TOKEN_DO_ANOTHER_EXERCISE
from apps.word_finding.models.user import User, ExerciseState

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
        self.assertIn("the first question", response_text)
        self.assertNotIn("next question", response_text)
        self.assertIn(" What's a pea?", response_text)

    def test_welcome_creates_user(self):
        QuestionFactory()
        self.assertEqual(User.objects.count(), 0)
        index(MockRequest())
        self.assertEqual(User.objects.count(), 1)

    def test_correct_answer(self):
        user = UserFactory(user_id='user')
        exercise = ExerciseFactory()
        question = QuestionFactory(exercise=exercise, answer='right answer')
        ExerciseStateFactory(
            user=user,
            exercise=exercise,
            current_question=question,
            completed=False,
        )

        response = index(MockRequest(text='right answer', user_id='user'))
        response_text = GoogleTestUtils.get_text_from_google_response(response)

        self.assertTrue(any(r in response_text for r in ("That's right! ", "Correct! ")))

    def test_incorrect_answer(self):
        user = UserFactory(user_id='user')
        exercise = ExerciseFactory()
        question = QuestionFactory(
            question='Who am I?',
            exercise=exercise,
            answer='right answer',
        )
        ExerciseStateFactory(
            user=user,
            exercise=exercise,
            current_question=question,
            completed=False,
        )

        response = index(MockRequest(text='wrong', user_id='user'))
        response_text = GoogleTestUtils.get_text_from_google_response(response)

        self.assertIn('incorrect', response_text)
        self.assertIn('Who am I?', response_text)

    def test_asks_next_question(self):
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

        self.assertIn("puzzling question", response_text)

    def test_exercise_completion(self):
        user = UserFactory(user_id='user')
        exercise = ExerciseFactory()
        question = QuestionFactory(exercise=exercise, answer='right answer')
        ExerciseStateFactory(
            user=user,
            exercise=exercise,
            current_question=question,
            completed=False,
        )

        response = index(MockRequest(text='right answer', user_id='user'))
        response_text = GoogleTestUtils.get_text_from_google_response(response)

        self.assertIn("finished", response_text)
        self.assertTrue(ExerciseState.objects.get().completed)
        self.assertEqual(
            TOKEN_DO_ANOTHER_EXERCISE,
            GoogleTestUtils.get_conversation_token_from_google_response(response))

    def test_do_another_exercise(self):
        UserFactory(user_id='user')
        QuestionFactory(question="What's a pea?")

        response = index(MockRequest(
            text='yes',
            user_id='user',
            conversation_token=TOKEN_DO_ANOTHER_EXERCISE,
        ))
        response_text = GoogleTestUtils.get_text_from_google_response(response)

        self.assertIn("let's go", response_text)
        self.assertIn(" What's a pea?", response_text)
        self.assertTrue(GoogleTestUtils.google_response_is_ask(response))

    def test_not_another_exercise(self):
        UserFactory(user_id='user')

        response = index(MockRequest(
            text='no',
            user_id='user',
            conversation_token=TOKEN_DO_ANOTHER_EXERCISE,
        ))
        response_text = GoogleTestUtils.get_text_from_google_response(response)

        self.assertIn("Goodbye", response_text)
        self.assertTrue(GoogleTestUtils.google_response_is_tell(response))


@pytest.mark.django_db
class IntegrationTests(TestCase):
    def test_basic_full_conversation(self):
        exercise = ExerciseFactory()
        QuestionFactory(exercise=exercise, question='question one', answer='answer one')
        QuestionFactory(exercise=exercise, question='question two', answer='answer two')

        # New user, starting the exercise and getting the first question
        response = index(MockRequest(user_id='user'))
        response_text = GoogleTestUtils.get_text_from_google_response(response)
        self.assertIn('Welcome', response_text)
        if 'question one' in response_text:
            self.assertNotIn('question two', response_text)
            first_question = 1
        else:
            self.assertIn('question two', response_text)
            first_question = 2

        # Test getting the answer wrong
        response = index(MockRequest(user_id='user', text='WRONG'))
        response_text = GoogleTestUtils.get_text_from_google_response(response)
        self.assertIn('incorrect', response_text)

        # Get the answer right, will get the next question
        answer = 'answer one' if first_question == 1 else 'answer two'
        response = index(MockRequest(user_id='user', text=answer))
        response_text = GoogleTestUtils.get_text_from_google_response(response)
        expected_question = 'question two' if first_question == 1 else 'question one'
        self.assertIn(expected_question, response_text)

        # Get the answer right, asks if we want to try another exercise
        answer = 'answer one' if first_question == 2 else 'answer two'
        response = index(MockRequest(user_id='user', text=answer))
        response_text = GoogleTestUtils.get_text_from_google_response(response)
        self.assertIn('Would you like to try another exercise', response_text)
        conversation_token = GoogleTestUtils.get_conversation_token_from_google_response(response)
        self.assertIsNotNone(conversation_token)

        # We don't want to try another, goodebye
        response = index(
            MockRequest(user_id='user', text='no', conversation_token=conversation_token))
        response_text = GoogleTestUtils.get_text_from_google_response(response)
        self.assertIn('Goodbye', response_text)
        self.assertTrue(GoogleTestUtils.google_response_is_tell(response))
