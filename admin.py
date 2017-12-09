from django.contrib import admin

from .models.excercise import Excercise, Question
from .models.user import User, ExcerciseState, AnswerGiven


admin.site.register(Excercise)
admin.site.register(Question)
admin.site.register(User)
admin.site.register(ExcerciseState)
admin.site.register(AnswerGiven)
