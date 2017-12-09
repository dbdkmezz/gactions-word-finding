from django.db import models

# from .clue import PhoneticClue


class Excercise(models.Model):
    name = models.CharField(max_length=32, unique=True)


class Question(models.Model):
    excercise = models.ForeignKey('Excercise', on_delete=models.CASCADE)
    question = models.TextField(unique=True)
    answer = models.CharField(max_length=32)

    class Meta:
        unique_together = (('excercise', 'question'),)

    # def clues(self):
    #     return PhoneticClue.objects.filter(question__id=self.id)
