import pytest

from django.test import TestCase

from apps.word_finding.models.user import ExcerciseState
from apps.word_finding.exceptions import NoExcerciseInProgress
from .factories import (
    UserFactory, AnswerGivenFactory, QuestionFactory, ExcerciseFactory, ExcerciseStateFactory,
)


@pytest.mark.django_db
class TestAnswerGivenModel(TestCase):
    def test_correct(self):
        question = QuestionFactory(answer='correct answer')
        incorrect_answer = AnswerGivenFactory(question=question, answer='incorrect answer')
        self.assertFalse(incorrect_answer.correct())

        correct_answer = AnswerGivenFactory(question=question, answer='correct answer')
        self.assertTrue(correct_answer.correct())


@pytest.mark.django_db
class TestUserModel(TestCase):
    def test_start_new_excercise(self):
        excercise = ExcerciseFactory()
        result = UserFactory().start_new_excercise()
        self.assertEqual(result, excercise)
        excercise_state = ExcerciseState.objects.all().get()
        self.assertEqual(excercise_state.excercise, excercise)
        self.assertIsNone(excercise_state.current_question)
        self.assertFalse(excercise_state.completed)

    def test_get_next_question_raises_if_no_excercise_in_progress(self):
        with self.assertRaises(NoExcerciseInProgress):
            UserFactory().get_next_question()

    def test_get_next_question(self):
        user = UserFactory()
        question = QuestionFactory()
        user.start_new_excercise()
        result = user.get_next_question()
        self.assertEqual(result, question.question)

    def test_check_answer_correct(self):
        user = UserFactory()
        excercise = ExcerciseFactory()
        question = QuestionFactory(excercise=excercise, answer='correct answer')
        ExcerciseStateFactory(
            user=user, excercise=excercise, current_question=question, completed=False)
        result = user.check_answer('correct answer')
        self.assertTrue(result)

    def test_check_answer_incorrect(self):
        user = UserFactory()
        excercise = ExcerciseFactory()
        question = QuestionFactory(excercise=excercise, answer='correct answer')
        ExcerciseStateFactory(
            user=user, excercise=excercise, current_question=question, completed=False)
        result = user.check_answer('wrong')
        self.assertFalse(result)
