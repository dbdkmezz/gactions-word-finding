from django.contrib import admin

from .models.exercise import Exercise, Question
from .models.user import User, ExerciseState, AnswerGiven


class QuestionAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Question._meta.fields]
    list_filter = ('exercise', )


class ExerciseAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Exercise._meta.fields]


class ExerciseStateAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ExerciseState._meta.fields]
    list_filter = ('user', 'exercise')


class UserAdmin(admin.ModelAdmin):
    list_display = [f.name for f in User._meta.fields]


class AnswerGivenAdmin(admin.ModelAdmin):
    @property
    def list_display(self):
        fields = [f.name for f in AnswerGiven._meta.fields]
        fields.append('correct')
        fields.append('exercise')
        return fields

    def exercise(self, obj):
        return obj.question.exercise

    def correct(self, obj):
        return obj.correct()
    correct.boolean = True


admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(ExerciseState, ExerciseStateAdmin)
admin.site.register(AnswerGiven, AnswerGivenAdmin)
