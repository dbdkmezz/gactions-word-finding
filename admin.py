from django.contrib import admin

from .models.exercise import Exercise, Question
from .models.user import User, ExerciseState, AnswerGiven


class QuestionAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Question._meta.fields]
    # fields = ['username', 'service', 'account_type', 'valid']


admin.site.register(Exercise)
admin.site.register(Question, QuestionAdmin)
admin.site.register(User)
admin.site.register(ExerciseState)
admin.site.register(AnswerGiven)
