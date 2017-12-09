# from django.db import models


# class Phoneme(models.Model):
#     sound_file_path = models.CharField(max_length=1024, unique=True)
#     ipa_symbol = models.CharField(max_length=1, unique=True)


# class PhoneticClue(models.Model):
#     question = models.ForeignKey('Question', on_delete=models.CASCADE)
#     prompt = models.TextField()
#     phoneme = models.ForeignKey('Phoneme', on_delete=models.CASCADE)

#     class Meta:
#         unique_together = (('question', 'prompt', 'phoneme'),)
