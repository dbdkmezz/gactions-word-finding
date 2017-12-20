from django.db import models

# from .cue import PhoneticCue


class Exercise(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    exercise = models.ForeignKey('Exercise', on_delete=models.CASCADE)
    question = models.TextField(unique=True)
    response = models.TextField(default='', blank=True)
    answer = models.TextField()

    class Meta:
        unique_together = (('exercise', 'question'),)

    def __str__(self):
        return self.question

    # def cues(self):
    #     return PhoneticCue.objects.filter(question__id=self.id)
