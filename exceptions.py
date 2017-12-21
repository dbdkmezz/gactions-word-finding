class NoExerciseInProgress(Exception):
    pass


class NoQuestionsRemaining(Exception):
    "There are no questions remaining in the current exercise."
    pass


class NoExercisesAvailable(Exception):
    "There are no exercises available which have not been disbaled."
    pass
