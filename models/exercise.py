import re

from django.db import models

# from .cue import PhoneticCue


class Exercise(models.Model):
    name = models.CharField(max_length=32, unique=True)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        result = self.name
        if not self.enabled:
            result += ' (DISABLED)'
        return result


class Question(models.Model):
    exercise = models.ForeignKey('Exercise', on_delete=models.CASCADE)
    question = models.TextField()
    response = models.TextField(default='', blank=True)
    answer = models.TextField()

    class Meta:
        unique_together = (('exercise', 'question'),)

    def __str__(self):
        return self.question

    def save(self, *args, **kwargs):
        self.answer = self.answer.lower()

        if re.search(r'[^a-z, ]', self.answer):
            raise Exception('Answers must not include any special characters')

        if re.search(r',[^ ]', self.answer):
            raise Exception((
                'To include multiple correct answers ensure that the answers are sparated by '
                'commas, with a space after each comma.'))

        if re.search(r'[^,]+ ', self.answer):
            raise Exception('Answers must not contain spaces.')

        super(Question, self).save(*args, **kwargs)

    @property
    def answers(self):
        return self.answer.split(', ')

    def model_answer(self, answer=None):
        if not answer:
            answer = self.answers[0]
        response = self.response if self.response else self.question
        if 'BLANK' in response:
            return response.replace('BLANK', answer)
        return '{} {}'.format(response, answer)

    # def cues(self):
    #     return PhoneticCue.objects.filter(question__id=self.id)
