from .models import RequestCount
from django.db import transaction

class RequestCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        with transaction.atomic(): #we use transaction to maintain atomicity
            request_count, created = RequestCount.objects.select_for_update().get_or_create(id=1)
            request_count.count += 1
            request_count.save()

        response = self.get_response(request)
        return response