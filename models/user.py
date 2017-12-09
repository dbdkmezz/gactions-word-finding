from django.db import models

from .excercise import Question


class User(models.Model):
    user_id = models.CharField(max_length=128, unique=True)


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


# class ClueGiven(models.Model):
#     quiz_state = models.ForeignKey('QuizState', on_delete=models.CASCADE)
#     question = models.ForeignKey('Question', on_delete=models.CASCADE)
#     clue = models.ForeignKey('PhoneticClue', on_delete=models.CASCADE)
