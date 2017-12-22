import random
import logging

from django.http import HttpResponse, JsonResponse

from libs.google_actions import AppResponse, AppRequest, NoJsonException

from .exceptions import NoQuestionsRemaining, MaxQuestionRetriesReached
from .models.user import User


logger = logging.getLogger(__name__)


# v1
# what happens if the user says nothing
#
# v2
# add emphasis to BLANK in questions -- https://developers.google.com/actions/reference/ssml
# random question order
# ask if they want to try a question again?
# add last_modified and date_created to appropriate models
# response better if don't understand response to do another exercise
# let the user choose the exercise
# optional question order


TOKEN_DO_ANOTHER_EXERCISE = 'DO_ANOTHER_EXERCISE'


def index(request):
    try:
        google_request = AppRequest(request)
    except NoJsonException:
        return HttpResponse("Hello world. You're at the word_finding index.")

    responses = []
    retry_question = False
    conversation_token = None
    first_question = False

    user, created = User.objects.get_or_create(user_id=google_request.user_id)

    if created:
        responses = _welcome(user, responses)
        first_question = True
    elif google_request.conversation_token == TOKEN_DO_ANOTHER_EXERCISE:
        if any(google_request.text in r for r in ('yes', 'ok')):
            user.start_new_exercise()
            responses.append("Alright, let's go!")
        else:
            return JsonResponse(AppResponse().tell('Goodbye'))
    elif not user.exercise_in_progress:
        user.start_new_exercise()
        responses.append("Welcome back. Let's start a new exercise.")
        first_question = True
    else:
        correct = user.check_answer(google_request.text)
        if correct:
            responses.append(random.choice(("That's right,", "Correct,")))
            responses.append('{}.'.format(user.get_model_answer(google_request.text)))
            user.reset_current_question()
        else:
            responses.append("I'm sorry, {} is incorrect.".format(google_request.text))
            try:
                question = user.retry_question()
            except MaxQuestionRetriesReached:
                responses.append('{}.'.format(user.get_model_answer(google_request.text)))
                user.reset_current_question()
                responses.append("Let's move on.")
            else:
                responses.append("Please try again.")
                responses.append(question)
                retry_question = True

    if not retry_question:
        responses, conversation_token = _get_next_question(
            user=user,
            responses=responses,
            first_question=first_question,
        )

    return JsonResponse(AppResponse().ask(
        ' '.join(responses),
        conversation_token=conversation_token,
    ))


def _welcome(user, responses):
    responses.append("Welcome to word finding practice.")
    user.start_new_exercise()
    return responses


def _get_next_question(user, responses, first_question):
    try:
        next_question = user.get_next_question()
    except NoQuestionsRemaining:
        user.complete_exercise()
        responses.append("Exercise finished. Well done!")
        responses.append("Would you like to try another exercise?")
        return responses, TOKEN_DO_ANOTHER_EXERCISE

    if first_question:
        responses.append("This is the first question:")
    else:
        responses.append("The next question is:")
    responses.append(next_question)
    return responses, None
