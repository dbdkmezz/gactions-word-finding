from django.db import models

# from .cue import PhoneticCue


class Excercise(models.Model):
    name = models.CharField(max_length=32, unique=True)


class Question(models.Model):
    excercise = models.ForeignKey('Excercise', on_delete=models.CASCADE)
    question = models.TextField(unique=True)
    answer = models.CharField(max_length=32)

    class Meta:
        unique_together = (('excercise', 'question'),)

    # def cues(self):
    #     return PhoneticCue.objects.filter(question__id=self.id)
