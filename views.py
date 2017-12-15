import logging

from django.http import HttpResponse, JsonResponse

from libs.google_actions import AppResponse, AppRequest, NoJsonException

from .models.user import User


logger = logging.getLogger(__name__)


def index(request):
    try:
        google_request = AppRequest(request)
    except NoJsonException:
        return HttpResponse("Hello world. You're at the word_finding index.")

    responses = []

    user, created = User.objects.get_or_create(user_id=google_request.user_id)
    if created:
        responses.append("Welcome to word finding practice.")
        responses.append("This is the first question:")
        user.start_new_excercise()
    else:
        correct = user.check_answer(google_request.text)
        if correct:
            responses.append("That's right!")
        else:
            responses.append("I'm sorry, that's incorrect.")
        # TODO: check if completed
        responses.append("The next question is:")

    responses.append(user.get_next_question())

    return JsonResponse(AppResponse().ask(' '.join(responses)))
