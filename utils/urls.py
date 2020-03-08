from django.urls import path

from .views import log


urlpatterns = [
    path('log/', log, name='log'),
]
