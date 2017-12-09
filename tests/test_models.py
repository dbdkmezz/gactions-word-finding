import pytest

from django.test import TestCase

from .factories import AnswerGivenFactory, QuestionFactory


@pytest.mark.django_db
class TestAnswerGivenModel(TestCase):
    def test_correct(self):
        question = QuestionFactory(answer='correct answer')
        incorrect_answer = AnswerGivenFactory(question=question, answer='incorrect answer')
        self.assertFalse(incorrect_answer.correct())

        correct_answer = AnswerGivenFactory(question=question, answer='correct answer')
        self.assertTrue(correct_answer.correct())
