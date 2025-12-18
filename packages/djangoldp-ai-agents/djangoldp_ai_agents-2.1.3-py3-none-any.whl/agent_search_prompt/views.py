from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name="dispatch")
class SearchPromptView(View):
    def post(self, request, *args, **kwargs):

        return HttpResponse("Not implemented")
