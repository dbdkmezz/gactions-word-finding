from django.db import models

from apps.word_finding.exceptions import NoExcerciseInProgress

from .excercise import Excercise, Question


class User(models.Model):
    user_id = models.CharField(max_length=128, unique=True)

    def start_new_excercise(self):
        if ExcerciseState.objects.filter(user=self, completed=False).exists():
            # exercise still in progress
            raise Exception

        excercises_completed = ExcerciseState.objects.filter(user=self)
        new_excercises = Excercise.objects.exclude(pk__in=excercises_completed)
        excercise = new_excercises.first()  # todo: make it random
        ExcerciseState.objects.create(
            user=self,
            excercise=excercise,
        )
        return excercise

    def check_answer(self, answer):
        state = ExcerciseState.objects.get(
            user=self,
            completed=False,
        )
        if state.current_question is None:
            raise Exception
        answer_given = AnswerGiven.objects.create(
            excercise_state=state,
            question=state.current_question,
            answer=answer,
        )
        return answer_given.correct()

    def get_next_question(self):
        try:
            state = ExcerciseState.objects.get(user=self, completed=False)
        except ExcerciseState.DoesNotExist:
            raise NoExcerciseInProgress
        if state.current_question is not None:
            raise Exception
        previous_answers = AnswerGiven.objects.filter(excercise_state=state)
        remaining_questions = Question.objects.filter(
            excercise=state.excercise
        ).exclude(pk__in=previous_answers)
        return remaining_questions.first().question


class ExcerciseState(models.Model):
    """A user's current state for a particular excercise.

    This includes excercisees which have been completed, so a user can have multiple states for the
    same excercise. But only one should currently be in progress.
    """
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    excercise = models.ForeignKey('Excercise', on_delete=models.CASCADE)
    current_question = models.ForeignKey('Question', on_delete=models.CASCADE, null=True)
    completed = models.BooleanField(default=False)


class AnswerGiven(models.Model):
    excercise_state = models.ForeignKey('ExcerciseState', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    answer = models.CharField(max_length=32)

    def correct(self):
        # Would be more efficient if answers were objects, then we wouldn't have to do a
        # string comparison here.
        # Alternatively, this bool could be part of the model, but that doesn't feel right.
        return any(Question.objects.filter(pk=self.question.pk, answer=self.answer))


# class CueGiven(models.Model):
#     quiz_state = models.ForeignKey('QuizState', on_delete=models.CASCADE)
#     question = models.ForeignKey('Question', on_delete=models.CASCADE)
#     clue = models.ForeignKey('PhoneticCue', on_delete=models.CASCADE)
