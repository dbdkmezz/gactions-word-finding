from django.db import models

from apps.word_finding.exceptions import (
    NoExerciseInProgress, NoQuestionsRemaining, NoExercisesAvailable,
)

from .exercise import Exercise, Question


class User(models.Model):
    user_id = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.user_id

    def get_current_exercise_state(self):
        try:
            return ExerciseState.objects.get(user=self, completed=False)
        except ExerciseState.DoesNotExist:
            raise NoExerciseInProgress

    def start_new_exercise(self):
        if ExerciseState.objects.filter(user=self, completed=False).exists():
            raise Exception("Can't start new exercise, exercise in progress.")

        exercises_completed = ExerciseState.objects.filter(user=self)
        new_exercises = Exercise.objects.exclude(pk__in=exercises_completed).exclude(enabled=False)
        if not new_exercises:
            raise NoExercisesAvailable
        exercise = new_exercises.first()  # todo: make it random
        ExerciseState.objects.create(
            user=self,
            exercise=exercise,
        )
        return exercise

    def check_answer(self, answer):
        state = self.get_current_exercise_state()
        if state.current_question is None:
            raise Exception("Can't check answer, there is no current question.")
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

    def retry_question(self):
        state = self.get_current_exercise_state()
        return state.current_question.question

    def get_next_question(self):
        state = self.get_current_exercise_state()
        if state.current_question:
            raise Exception("Can't get next question, there already is a current question.")

        previous_answers = AnswerGiven.objects.filter(exercise_state=state)
        questions_answered = (a.question.pk for a in previous_answers)
        question = Question.objects.filter(
            exercise=state.exercise
        ).exclude(
            pk__in=questions_answered
        ).first()

        if not question:
            raise NoQuestionsRemaining

        state.current_question = question
        state.save()
        return question.question

    def complete_exercise(self):
        num_updated = (
            ExerciseState.objects.filter(user=self, completed=False).update(completed=True))
        if num_updated != 1:
            raise Exception(
                "There were multiple exercises not completed for user {}".format(self))


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
        return Question.objects.get(pk=self.question.pk).answer.lower() == self.answer.lower()


# class CueGiven(models.Model):
#     quiz_state = models.ForeignKey('QuizState', on_delete=models.CASCADE)
#     question = models.ForeignKey('Question', on_delete=models.CASCADE)
#     clue = models.ForeignKey('PhoneticCue', on_delete=models.CASCADE)
