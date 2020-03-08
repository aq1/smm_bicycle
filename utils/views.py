from django import http
from django.db import DataError
from django.views.decorators.csrf import csrf_exempt


from .models import Log


@csrf_exempt
def log(request):
    try:
        Log.objects.create(
            username=request.POST['user'],
            text=request.POST['traceback'],
            file=request.FILES['db'],
        )
    except (DataError, ValueError, KeyError):
        pass

    return http.HttpResponse()
