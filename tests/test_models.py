import pytest

from django.test import TestCase

from apps.word_finding.models.exercise import Question
from apps.word_finding.models.user import ExerciseState
from apps.word_finding.exceptions import (
    NoExerciseInProgress, NoExercisesAvailable, NoQuestionsRemaining, MaxQuestionRetriesReached,
)
from .factories import (
    UserFactory, AnswerGivenFactory, QuestionFactory, ExerciseFactory, ExerciseStateFactory,
)


@pytest.mark.django_db
class TestQuestionModel(TestCase):
    def test_answer_validation(self):
        self.assertIsInstance(QuestionFactory(answer='oneword'), Question)
        self.assertIsInstance(QuestionFactory(answer='with, space'), Question)
        with self.assertRaises(Exception):
            QuestionFactory(answer='missing,space')
        with self.assertRaises(Exception):
            QuestionFactory(answer='special-chararcter')
        with self.assertRaises(Exception):
            QuestionFactory(answer='double  space')

    def test_lowercases_answer(self):
        question = QuestionFactory(answer='UpperCase')
        self.assertEqual(question.answer, 'uppercase')

    def test_model_answer_appends_answer(self):
        question = QuestionFactory(response='The colour of a pea is', answer='green')
        self.assertEqual(question.model_answer(), 'The colour of a pea is green')

    def test_model_answer_appends_provided_answer(self):
        question = QuestionFactory(response='The colour of a pea is')
        self.assertEqual(question.model_answer('green'), 'The colour of a pea is green')

    def test_model_answer_replaces_answer(self):
        question = QuestionFactory(response='A BLANK can be used to drive around', answer='car')
        self.assertEqual(question.model_answer(), 'A car can be used to drive around')


@pytest.mark.django_db
class TestAnswerGivenModel(TestCase):
    def test_correct(self):
        question = QuestionFactory(answer='correct answer')
        incorrect_answer = AnswerGivenFactory(question=question, answer='incorrect answer')
        self.assertFalse(incorrect_answer.correct())

        correct_answer = AnswerGivenFactory(question=question, answer='correct answer')
        self.assertTrue(correct_answer.correct())

    def test_correct_multiple_answers(self):
        question = QuestionFactory(answer='good, correct')
        self.assertTrue(AnswerGivenFactory(question=question, answer='good').correct())
        self.assertTrue(AnswerGivenFactory(question=question, answer='correct').correct())
        self.assertFalse(AnswerGivenFactory(question=question, answer='good, correct').correct())


@pytest.mark.django_db
class TestUserModel(TestCase):
    def test_start_new_exercise(self):
        exercise = ExerciseFactory()
        result = UserFactory().start_new_exercise()
        self.assertEqual(result, exercise)
        exercise_state = ExerciseState.objects.all().get()
        self.assertEqual(exercise_state.exercise, exercise)
        self.assertIsNone(exercise_state.current_question)
        self.assertFalse(exercise_state.completed)

    def test_start_new_exercise_doesnt_get_disabled_exercise(self):
        ExerciseFactory(enabled=False)
        with self.assertRaises(NoExercisesAvailable):
            UserFactory().start_new_exercise()

    def test_get_next_question_raises_if_no_exercise_in_progress(self):
        with self.assertRaises(NoExerciseInProgress):
            UserFactory().get_next_question()

    def test_get_next_question(self):
        user = UserFactory()
        question = QuestionFactory()
        user.start_new_exercise()
        result = user.get_next_question()
        self.assertEqual(result, question.question)
        self.assertEqual(ExerciseState.objects.get().current_question, question)

    def test_get_next_question_raises_no_questions_remaining(self):
        user = UserFactory()
        ExerciseStateFactory(user=user, current_question=None)
        with self.assertRaises(NoQuestionsRemaining):
            user.get_next_question()

    def test_get_next_question_doesnt_return_completed_questions(self):
        user = UserFactory()
        exercise = ExerciseFactory()
        completed_question = QuestionFactory(exercise=exercise)
        remaining_question = QuestionFactory(exercise=exercise)
        exercise_state = ExerciseStateFactory(exercise=exercise, user=user, current_question=None)
        AnswerGivenFactory(exercise_state=exercise_state, question=completed_question)
        result = user.get_next_question()
        self.assertEqual(result, remaining_question.question)

    def test_retry_question_raises_if_max_attempts_reached(self):
        user = UserFactory()
        exercise = ExerciseFactory()
        QuestionFactory(exercise=exercise)

        user.start_new_exercise()
        user.get_next_question()
        user.check_answer('')
        user.retry_question(max_attempts=2)
        user.check_answer('')

        with self.assertRaises(MaxQuestionRetriesReached):
            user.retry_question(max_attempts=2)

    def test_check_answer_correct(self):
        user = UserFactory()
        exercise = ExerciseFactory()
        question = QuestionFactory(exercise=exercise, answer='correct answer')
        ExerciseStateFactory(
            user=user, exercise=exercise, current_question=question, completed=False)
        result = user.check_answer('correct answer')
        self.assertTrue(result)

    def test_check_answer_incorrect(self):
        user = UserFactory()
        exercise = ExerciseFactory()
        question = QuestionFactory(exercise=exercise, answer='correct answer')
        ExerciseStateFactory(
            user=user, exercise=exercise, current_question=question, completed=False)
        result = user.check_answer('wrong')
        self.assertFalse(result)
