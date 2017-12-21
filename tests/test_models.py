import pytest

from django.test import TestCase

from apps.word_finding.models.user import ExerciseState
from apps.word_finding.exceptions import (
    NoExerciseInProgress, NoExercisesAvailable, NoQuestionsRemaining,
)
from .factories import (
    UserFactory, AnswerGivenFactory, QuestionFactory, ExerciseFactory, ExerciseStateFactory,
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
