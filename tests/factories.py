from factory import DjangoModelFactory, SubFactory, fuzzy

from apps.word_finding.models.user import User, ExcerciseState, AnswerGiven
from apps.word_finding.models.excercise import Excercise, Question


class ExcerciseFactory(DjangoModelFactory):
    class Meta:
        model = Excercise

    name = fuzzy.FuzzyText(length=32)


class QuestionFactory(DjangoModelFactory):
    class Meta:
        model = Question

    excercise = SubFactory(ExcerciseFactory)
    question = fuzzy.FuzzyText(length=128)
    answer = fuzzy.FuzzyText(length=32)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    user_id = fuzzy.FuzzyText(length=100)


class ExcerciseStateFactory(DjangoModelFactory):
    class Meta:
        model = ExcerciseState

    user = SubFactory(UserFactory)
    excercise = SubFactory(ExcerciseFactory)
    current_question = SubFactory(QuestionFactory)
    completed = fuzzy.FuzzyChoice((True, False))


class AnswerGivenFactory(DjangoModelFactory):
    class Meta:
        model = AnswerGiven

    excercise_state = SubFactory(ExcerciseStateFactory)
    question = SubFactory(QuestionFactory)
    answer = fuzzy.FuzzyText(length=32)
