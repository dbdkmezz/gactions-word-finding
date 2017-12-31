import pytest

from django.test import TestCase
from django.http import HttpResponse

from libs.google_actions.tests.mocks import MockRequest
from libs.google_actions.tests.utils import Utils as GoogleTestUtils

from apps.word_finding.views import index, TOKEN_DO_ANOTHER_EXERCISE
from apps.word_finding.models.user import User, ExerciseState

from .factories import (
    ExerciseFactory, QuestionFactory, UserFactory, ExerciseStateFactory, AnswerGivenFactory,
)


@pytest.mark.django_db
class TestViews(TestCase):
    def test_hello_world_if_not_json(self):
        result = index(MockRequest(body='NOT JSON'))
        self.assertIsInstance(result, HttpResponse)
        self.assertIn("Hello world", str(result.content))

    def test_welcome_if_new_user(self):
        QuestionFactory(question="What's a pea?")
        response = _make_request_and_return_text()
        self.assertIn('Welcome. ', response)
        self.assertIn("the first question", response)
        self.assertNotIn("next question", response)
        self.assertIn(" What's a pea?", response)

    def test_welcome_creates_user(self):
        QuestionFactory()
        self.assertEqual(User.objects.count(), 0)
        index(MockRequest())
        self.assertEqual(User.objects.count(), 1)

    def test_correct_answer(self):
        exercise = ExerciseFactory()
        question = QuestionFactory(
            exercise=exercise,
            answer='rightanswer',
            question='the question',
            response='response',
        )
        ExerciseStateFactory(
            user=UserFactory(user_id='user'),
            exercise=exercise,
            current_question=question,
            completed=False,
        )

        response = _make_request_and_return_text(text='rightanswer', user_id='user')

        self.assertTrue(any(r in response for r in ("That's right, ", "Correct, ")))
        self.assertIn('response', response)
        self.assertIn('rightanswer', response)

    def test_incorrect_answer(self):
        user = UserFactory(user_id='user')
        exercise = ExerciseFactory()
        question = QuestionFactory(
            question='Who am I?',
            exercise=exercise,
            answer='right',
        )
        ExerciseStateFactory(
            user=user,
            exercise=exercise,
            current_question=question,
            completed=False,
        )

        response = _make_request_and_return_text(text='wrong', user_id='user')

        self.assertIn('incorrect', response)
        self.assertIn('Who am I?', response)

    def test_asks_next_question(self):
        user = UserFactory(user_id='user')
        exercise = ExerciseFactory()
        question = QuestionFactory(exercise=exercise, answer='rightanswer')
        QuestionFactory(exercise=exercise, question='puzzling question')
        ExerciseStateFactory(
            user=user,
            exercise=exercise,
            current_question=question,
            completed=False,
        )
        response = _make_request_and_return_text(text='rightanswer', user_id='user')
        self.assertIn("puzzling question", response)

    def test_returning_user(self):
        UserFactory(user_id='user')
        QuestionFactory()
        response = _make_request_and_return_text(user_id='user')
        self.assertIn("Welcome back", response)
        self.assertNotIn("next question", response)

    def test_max_question_retries_reached(self):
        exercise = ExerciseFactory()
        question = QuestionFactory(exercise=exercise)
        next_question = QuestionFactory(exercise=exercise)
        state = ExerciseStateFactory(
            user=UserFactory(user_id='user'),
            exercise=exercise,
            current_question=question,
            completed=False,
        )
        AnswerGivenFactory(exercise_state=state, question=question)
        AnswerGivenFactory(exercise_state=state, question=question)
        AnswerGivenFactory(exercise_state=state, question=question)

        response = _make_request_and_return_text(text='wrong answer', user_id='user')

        self.assertIn('incorrect', response)
        self.assertIn('move on', response)
        self.assertNotIn(question.question, response)
        self.assertIn(next_question.question, response)

    def test_exercise_completion(self):
        exercise = ExerciseFactory()
        ExerciseStateFactory(
            user=UserFactory(user_id='user'),
            exercise=exercise,
            current_question=QuestionFactory(exercise=exercise, answer='right'),
            completed=False,
        )

        response = index(MockRequest(text='right', user_id='user'))
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
        QuestionFactory(exercise=exercise, question='question one', answer='one')
        QuestionFactory(exercise=exercise, question='question two', answer='two')

        # New user, starting the exercise and getting the first question
        response = _make_request_and_return_text(user_id='user')
        self.assertIn('Welcome', response)
        if 'question one' in response:
            self.assertNotIn('question two', response)
            first_question = 1
        else:
            self.assertIn('question two', response)
            first_question = 2

        # Test getting the answer wrong
        response = _make_request_and_return_text(user_id='user', text='WRONG')
        self.assertIn('incorrect', response)

        # Get the answer right, will get the next question
        answer = 'one' if first_question == 1 else 'two'
        response = _make_request_and_return_text(user_id='user', text=answer)
        expected_question = 'question two' if first_question == 1 else 'question one'
        self.assertIn(expected_question, response)

        # Get the answer right, asks if we want to try another exercise
        answer = 'one' if first_question == 2 else 'two'
        raw_response = index(MockRequest(user_id='user', text=answer))
        response_text = GoogleTestUtils.get_text_from_google_response(raw_response)
        self.assertIn('Would you like to try another exercise', response_text)
        conversation_token = (
            GoogleTestUtils.get_conversation_token_from_google_response(raw_response))
        self.assertIsNotNone(conversation_token)

        # We don't want to try another, goodebye
        raw_response = index(
            MockRequest(user_id='user', text='no', conversation_token=conversation_token))
        response_text = GoogleTestUtils.get_text_from_google_response(raw_response)
        self.assertIn('Goodbye', response_text)
        self.assertTrue(GoogleTestUtils.google_response_is_tell(raw_response))


def _make_request_and_return_text(text=None, user_id=None, conversation_token=None):
    response = index(
        MockRequest(text=text, user_id=user_id, conversation_token=conversation_token))
    return GoogleTestUtils.get_text_from_google_response(response)
