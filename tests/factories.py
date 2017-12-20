from factory import DjangoModelFactory, SubFactory, fuzzy

from apps.word_finding.models.user import User, ExerciseState, AnswerGiven
from apps.word_finding.models.exercise import Exercise, Question


class ExerciseFactory(DjangoModelFactory):
    class Meta:
        model = Exercise

    name = fuzzy.FuzzyText(length=32)


class QuestionFactory(DjangoModelFactory):
    class Meta:
        model = Question

    exercise = SubFactory(ExerciseFactory)
    question = fuzzy.FuzzyText(length=128)
    answer = fuzzy.FuzzyText(length=32)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    user_id = fuzzy.FuzzyText(length=100)


class ExerciseStateFactory(DjangoModelFactory):
    class Meta:
        model = ExerciseState

    user = SubFactory(UserFactory)
    exercise = SubFactory(ExerciseFactory)
    current_question = SubFactory(QuestionFactory)
    completed = fuzzy.FuzzyChoice((True, False))


class AnswerGivenFactory(DjangoModelFactory):
    class Meta:
        model = AnswerGiven

    exercise_state = SubFactory(ExerciseStateFactory)
    question = SubFactory(QuestionFactory)
    answer = fuzzy.FuzzyText(length=32)
