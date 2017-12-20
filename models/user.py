from django.db import models

from apps.word_finding.exceptions import NoExerciseInProgress

from .exercise import Exercise, Question


class User(models.Model):
    user_id = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.user_id

    def start_new_exercise(self):
        if ExerciseState.objects.filter(user=self, completed=False).exists():
            # exercise still in progress
            raise Exception

        exercises_completed = ExerciseState.objects.filter(user=self)
        new_exercises = Exercise.objects.exclude(pk__in=exercises_completed)
        exercise = new_exercises.first()  # todo: make it random
        ExerciseState.objects.create(
            user=self,
            exercise=exercise,
        )
        return exercise

    def check_answer(self, answer):
        state = ExerciseState.objects.get(
            user=self,
            completed=False,
        )
        if state.current_question is None:
            raise Exception
        answer_given = AnswerGiven.objects.create(
            exercise_state=state,
            question=state.current_question,
            answer=answer,
        )
        correct = answer_given.correct()
        if correct:
            state.current_question = None
            state.save()
        return correct

    def get_next_question(self):
        try:
            state = ExerciseState.objects.get(user=self, completed=False)
        except ExerciseState.DoesNotExist:
            raise NoExerciseInProgress
        if state.current_question is not None:
            raise Exception
        previous_answers = AnswerGiven.objects.filter(exercise_state=state)
        remaining_questions = Question.objects.filter(
            exercise=state.exercise
        ).exclude(pk__in=previous_answers)
        return remaining_questions.first().question


class ExerciseState(models.Model):
    """A user's current state for a particular exercise.

    This includes exercisees which have been completed, so a user can have multiple states for the
    same exercise. But only one should currently be in progress.
    """
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    exercise = models.ForeignKey('Exercise', on_delete=models.CASCADE)
    current_question = models.ForeignKey('Question', on_delete=models.CASCADE, null=True)
    completed = models.BooleanField(default=False)


class AnswerGiven(models.Model):
    exercise_state = models.ForeignKey('ExerciseState', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    answer = models.CharField(max_length=32)

    def correct(self):
        # Would be more efficient if answers were objects, then we wouldn't have to do a
        # string comparison here.
        # Alternatively, this bool could be part of the model, but that doesn't feel right.
        return Question.objects.get(pk=self.question.pk).answer == self.answer


# class CueGiven(models.Model):
#     quiz_state = models.ForeignKey('QuizState', on_delete=models.CASCADE)
#     question = models.ForeignKey('Question', on_delete=models.CASCADE)
#     clue = models.ForeignKey('PhoneticCue', on_delete=models.CASCADE)
