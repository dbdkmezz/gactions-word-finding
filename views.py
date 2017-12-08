import logging

from django.http import HttpResponse, JsonResponse

from libs.google_actions import AppResponse, AppRequest, NoJsonException


logger = logging.getLogger(__name__)


def index(request):
    try:
        google_request = AppRequest(request)
    except NoJsonException:
        return HttpResponse("Hello world. You're at the word_finding index.")

    query = google_request.text
    return JsonResponse(AppResponse().ask("Hello there google."))
